import logging
from flask import Flask, render_template, request, jsonify
from config import Config
from utils import InputValidator, ValidationError, AstroCalculator
from utils.geo_format import format_latitude, format_longitude, format_coordinates, format_arc_dms
from core.sign_qualities import get_sign_symbol
from core.interpretation_guide import (
    render_interpretation_guide_html,
    render_interpretation_guide_for_prompt,
)
from services import AIService
from prompts import ASTRO_PROMPT, TRANSIT_PROMPT
from data import get_all_cities
from database import save_birth_chart, get_birth_chart, get_all_birth_charts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

try:
    Config.validate()
    app.config.from_object(Config)
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

# Initialize services
ai_service = AIService()


@app.template_filter('dms_lat')
def dms_lat_filter(value):
    """Jinja filter: decimal latitude -> DMS string."""
    try:
        return format_latitude(float(value))
    except (TypeError, ValueError):
        return '—'


@app.template_filter('dms_lon')
def dms_lon_filter(value):
    """Jinja filter: decimal longitude -> DMS string."""
    try:
        return format_longitude(float(value))
    except (TypeError, ValueError):
        return '—'


@app.template_filter('dms_coords')
def dms_coords_filter(coords):
    """Jinja filter: (lat, lon) tuple -> combined DMS string."""
    try:
        lat, lon = coords
        return format_coordinates(float(lat), float(lon))
    except (TypeError, ValueError):
        return '—'


@app.template_filter('dms_arc')
def dms_arc_filter(value):
    """Jinja filter: decimal arc degrees -> DMS string (ecliptic/aspects)."""
    try:
        return format_arc_dms(float(value))
    except (TypeError, ValueError):
        return '—'


@app.route("/")
def index():
    """Home page with birth chart form"""
    swiss_available = AstroCalculator.is_available()
    cities = get_all_cities()
    return render_template("index.html", swiss=swiss_available, cities=cities)


@app.route("/calculate", methods=["POST"])
def calculate():
    """Calculate Swiss Ephemeris data and show results"""
    try:
        # Get form data
        name = request.form.get("name", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        place = request.form.get("place", "").strip()
        solar_city = request.form.get("solar_city", "").strip()
        vision = request.form.get("vision", "").strip()
        use_swiss = request.form.get("swiss_ephemeris", "no") == "yes"
        
        # Validate inputs
        try:
            validated = InputValidator.validate_all(name, date, time, place, vision)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return render_template("error.html", error=str(e))
        
        # Always calculate astronomical data with Swiss Ephemeris
        astro_html = None
        birth_data_info = None
        chart_data_raw = None
        
        if not AstroCalculator.is_available():
            return render_template("error.html", error="Swiss Ephemeris در دسترس نیست. لطفاً کتابخانه‌های مورد نیاز را نصب کنید.")
        
        try:
            logger.info("Calculating chart with Swiss Ephemeris")
            birth_data = AstroCalculator.prepare_birth_data(
                validated['date'],
                validated['time'],
                validated['place']
            )
            # Add person info to birth_data for HTML output
            birth_data['name'] = validated['name']
            birth_data['vision'] = validated['vision']
            birth_data['jalali_date'] = validated['date']
            birth_data['local_time'] = validated['time']
            birth_data['solar_city'] = solar_city if solar_city else place  # Use birth city if not specified
            
            result = AstroCalculator.calculate_chart(birth_data)
            astro_html = result['html']  # HTML with chart image for display
            astro_html_for_ai = result['html_for_ai']  # HTML without chart image for AI
            chart_data_raw = result['chart_data']
            birth_data_info = birth_data
            if chart_data_raw:
                birth_data_info['is_diurnal'] = chart_data_raw.get('is_diurnal', True)
                birth_data_info['sect_fa'] = chart_data_raw.get('sect_fa', '')
                asc = chart_data_raw.get('houses', {}).get('ascendant', {})
                birth_data_info['asc_sign_fa'] = asc.get('sign_fa', '')
                birth_data_info['asc_sign_symbol'] = get_sign_symbol(asc.get('sign_fa', ''))
            logger.info("Chart calculation successful")
        except Exception as e:
            logger.error(f"Swiss Ephemeris calculation failed: {e}")
            return render_template("error.html", error=f"خطا در محاسبات نجومی: {str(e)}")
        
        # Show calculation results
        return render_template(
            "calculation.html",
            name=validated['name'],
            date=validated['date'],
            time=validated['time'],
            place=validated['place'],
            solar_city=solar_city,
            vision=validated['vision'],
            use_swiss=use_swiss,
            astro_data=astro_html,  # HTML with chart image for display
            astro_data_for_ai=astro_html_for_ai,  # Plain text chart data for view-prompt
            birth_data=birth_data_info,
            interpretation_guide=render_interpretation_guide_html(),
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in calculate: {e}")
        return render_template("error.html", error="خطای غیرمنتظره رخ داد. لطفاً دوباره تلاش کنید.")


@app.route("/calculate-transit", methods=["POST"])
def calculate_transit():
    """Calculate full moment transits against natal chart."""
    try:
        name = request.form.get("name", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        place = request.form.get("place", "").strip()
        vision = request.form.get("vision", "").strip()

        try:
            validated = InputValidator.validate_all(name, date, time, place, vision)
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return render_template("error.html", error=str(e))

        if not AstroCalculator.is_available():
            return render_template(
                "error.html",
                error="Swiss Ephemeris در دسترس نیست. لطفاً کتابخانه‌های مورد نیاز را نصب کنید.",
            )

        try:
            birth_data = AstroCalculator.prepare_birth_data(
                validated['date'],
                validated['time'],
                validated['place'],
            )
            birth_data['name'] = validated['name']
            birth_data['vision'] = validated['vision']
            birth_data['jalali_date'] = validated['date']
            birth_data['local_time'] = validated['time']

            result = AstroCalculator.calculate_transit(birth_data)
            birth_data_info = birth_data
            chart_data_raw = result['chart_data']
            if chart_data_raw:
                birth_data_info['is_diurnal'] = chart_data_raw.get('is_diurnal', True)
                asc = chart_data_raw.get('houses', {}).get('ascendant', {})
                birth_data_info['asc_sign_fa'] = asc.get('sign_fa', '')
                birth_data_info['asc_sign_symbol'] = get_sign_symbol(asc.get('sign_fa', ''))

            return render_template(
                "transit_calculation.html",
                name=validated['name'],
                date=validated['date'],
                time=validated['time'],
                place=validated['place'],
                vision=validated['vision'],
                astro_data=result['html'],
                astro_data_for_ai=result['html_for_ai'],
                birth_data=birth_data_info,
                current_date_info=result['current_date_info'],
            )
        except Exception as e:
            logger.error(f"Transit calculation failed: {e}")
            return render_template("error.html", error=f"خطا در محاسبات ترانزیت: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error in calculate_transit: {e}")
        return render_template("error.html", error="خطای غیرمنتظره رخ داد. لطفاً دوباره تلاش کنید.")


@app.route("/view-prompt", methods=["POST"])
def view_prompt():
    """Display the complete AI prompt in a new page for manual copying"""
    try:
        # Get form data
        name = request.form.get("name", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        place = request.form.get("place", "").strip()
        vision = request.form.get("vision", "").strip()
        astro_data = request.form.get("astro_data", "")
        
        prompt = ASTRO_PROMPT.format(
            astro_data=astro_data,
            vision=vision if vision else "تحلیل جامع زایچه",
            interpretation_guide=render_interpretation_guide_for_prompt(),
        )
        # Render template with prompt text
        return render_template(
            'view_prompt.html',
            name=name,
            date=date,
            time=time,
            place=place,
            vision=vision,
            prompt_text=prompt,
            prompt_title='پرامپت تحلیل زایچه تولد و سولار',
            prompt_subtitle='خروجی: دو بخش (تولد + سولار) — متن روان، بدون HTML',
        )

    except Exception as e:
        logger.error(f"View prompt failed: {e}")
        return f"خطا در نمایش پرامپت: {str(e)}", 500


@app.route("/view-transit-prompt", methods=["POST"])
def view_transit_prompt():
    """Display transit analysis prompt for manual copying."""
    try:
        name = request.form.get("name", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        place = request.form.get("place", "").strip()
        vision = request.form.get("vision", "").strip()
        transit_data = request.form.get("transit_data", "")

        prompt = TRANSIT_PROMPT.format(
            transit_data=transit_data,
            vision=vision if vision else "تحلیل ترانزیت لحظه",
            interpretation_guide=render_interpretation_guide_for_prompt(),
        )
        return render_template(
            'view_prompt.html',
            name=name,
            date=date,
            time=time,
            place=place,
            vision=vision,
            prompt_text=prompt,
            prompt_title='پرامپت تحلیل ترانزیت لحظه',
            prompt_subtitle='خروجی: تحلیل وضعیت فعلی — متن روان، بدون HTML',
        )
    except Exception as e:
        logger.error(f"View transit prompt failed: {e}")
        return f"خطا در نمایش پرامپت ترانزیت: {str(e)}", 500


@app.route("/save", methods=["POST"])
def save():
    """Save birth chart to database"""
    try:
        import json
        
        # Get data from form
        name = request.form.get("name", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()
        place = request.form.get("place", "").strip()
        vision = request.form.get("vision", "").strip()
        astro_data = request.form.get("astro_data", "")
        ai_analysis = request.form.get("ai_analysis", "")
        birth_data_json = request.form.get("birth_data", "{}")
        
        # Parse birth data
        try:
            birth_data = json.loads(birth_data_json) if birth_data_json else {}
        except:
            birth_data = {}
        
        # Prepare data for database
        chart_data = {
            'name': name,
            'birth_date_persian': date,
            'birth_date_gregorian': birth_data.get('gregorian_full', ''),
            'birth_time_local': time,
            'birth_time_utc': birth_data.get('utc_time', ''),
            'city_name': place,
            'latitude': birth_data.get('lat', 0),
            'longitude': birth_data.get('lon', 0),
            'timezone': birth_data.get('timezone', 'Asia/Tehran'),
            'astro_data': astro_data,
            'ai_analysis': ai_analysis,
            'vision': vision
        }
        
        # Save to database
        chart_id = save_birth_chart(chart_data)
        
        return jsonify({
            'success': True,
            'message': 'زایچه با موفقیت ذخیره شد',
            'chart_id': chart_id
        })
        
    except Exception as e:
        logger.error(f"Error saving chart: {e}")
        return jsonify({
            'success': False,
            'message': f'خطا در ذخیره‌سازی: {str(e)}'
        }), 500


@app.route("/charts")
def charts():
    """View all saved charts"""
    try:
        all_charts = get_all_birth_charts()
        return render_template("charts.html", charts=all_charts)
    except Exception as e:
        logger.error(f"Error loading charts: {e}")
        return render_template("error.html", error="خطا در بارگذاری زایچه‌ها")


@app.route("/chart/<int:chart_id>")
def view_chart(chart_id):
    """View a specific chart"""
    try:
        chart = get_birth_chart(chart_id)
        if not chart:
            return render_template("error.html", error="زایچه یافت نشد")
        return render_template("view_chart.html", chart=chart)
    except Exception as e:
        logger.error(f"Error loading chart: {e}")
        return render_template("error.html", error="خطا در بارگذاری زایچه")


@app.route("/simplify", methods=["POST"])
def simplify():
    """Simplify astrological text"""
    try:
        text = request.form.get("text", "")
        
        if not text:
            return render_template("error.html", error="متن برای ساده‌سازی یافت نشد")
        
        try:
            simple = ai_service.simplify_text(text)
            return render_template("result.html", result=simple)
        except Exception as e:
            logger.error(f"Text simplification failed: {e}")
            return render_template("error.html", error=f"خطا در ساده‌سازی متن: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error in simplify: {e}")
        return render_template("error.html", error="خطای غیرمنتظره رخ داد")


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template("error.html", error="صفحه مورد نظر یافت نشد"), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {e}")
    return render_template("error.html", error="خطای سرور رخ داد"), 500


# ============================================================================
# Cities Management Routes
# ============================================================================

@app.route("/cities-admin")
def cities_admin():
    """Cities management page"""
    from database import get_all_cities_detailed
    cities = get_all_cities_detailed()
    return render_template("cities_admin.html", cities=cities)


@app.route("/api/cities", methods=["GET"])
def get_cities_api():
    """Get all cities (API)"""
    from database import get_all_cities_detailed
    try:
        cities = get_all_cities_detailed()
        return jsonify({"success": True, "cities": cities})
    except Exception as e:
        logger.error(f"Error getting cities: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/cities", methods=["POST"])
def add_city_api():
    """Add a new city (API)"""
    from database import add_city
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['name_fa', 'name_en', 'latitude', 'longitude']
        for field in required:
            if field not in data:
                return jsonify({"success": False, "message": f"فیلد {field} الزامی است"}), 400
        
        city_id = add_city(
            name_fa=data['name_fa'],
            name_en=data['name_en'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            timezone=data.get('timezone', 'Asia/Tehran')
        )
        
        if city_id:
            return jsonify({"success": True, "message": "شهر با موفقیت اضافه شد", "city_id": city_id})
        else:
            return jsonify({"success": False, "message": "شهر با این نام قبلاً وجود دارد"}), 400
            
    except Exception as e:
        logger.error(f"Error adding city: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/cities/<int:city_id>", methods=["PUT"])
def update_city_api(city_id):
    """Update a city (API)"""
    from database import update_city
    try:
        data = request.get_json()
        
        success = update_city(
            city_id=city_id,
            name_fa=data.get('name_fa'),
            name_en=data.get('name_en'),
            latitude=float(data['latitude']) if 'latitude' in data else None,
            longitude=float(data['longitude']) if 'longitude' in data else None,
            timezone=data.get('timezone')
        )
        
        if success:
            return jsonify({"success": True, "message": "شهر با موفقیت ویرایش شد"})
        else:
            return jsonify({"success": False, "message": "خطا در ویرایش شهر"}), 400
            
    except Exception as e:
        logger.error(f"Error updating city: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/cities/<int:city_id>", methods=["DELETE"])
def delete_city_api(city_id):
    """Delete a city (API)"""
    from database import delete_city
    try:
        success = delete_city(city_id)
        
        if success:
            return jsonify({"success": True, "message": "شهر با موفقیت حذف شد"})
        else:
            return jsonify({"success": False, "message": "خطا در حذف شهر"}), 400
            
    except Exception as e:
        logger.error(f"Error deleting city: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    logger.info(f"Starting application on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
