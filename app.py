import json
import logging
import secrets
from urllib.parse import urlsplit

from flask import Flask, render_template, request, jsonify, redirect, url_for, abort, make_response, session, flash
from itsdangerous import BadData, URLSafeTimedSerializer
from config import Config
from utils import InputValidator, ValidationError, AstroCalculator
from utils.geo_format import format_latitude, format_longitude, format_coordinates, format_arc_dms
from core.sign_qualities import get_sign_symbol
from core.interpretation_guide import (
    render_interpretation_guide_html,
    render_interpretation_guide_for_prompt,
)
from services import AIService, AIConfigError, format_analysis_html
from services.chart_summary import SUMMARY_SECTIONS, generate_chart_summary
from prompts import ASTRO_PROMPT, TRANSIT_PROMPT, prompt_when, safe_prompt_value
from data import get_all_cities
from database import (
    save_birth_chart, get_birth_chart, get_all_birth_charts, save_ai_settings, update_birth_chart_analysis,
    delete_birth_chart, update_birth_details, StaleBirthChartError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
ai_service = AIService()
# The public development key must not sign user data.
summary_secret = app.config["SECRET_KEY"]
if not summary_secret or summary_secret == 'change-me-in-production':
    summary_secret = secrets.token_hex(32)
app.secret_key = summary_secret
summary_chart_signer = URLSafeTimedSerializer(summary_secret, salt='summary-chart-v1')
summary_draft_signer = URLSafeTimedSerializer(summary_secret, salt='summary-draft-v1')
archive_summary_signer = URLSafeTimedSerializer(summary_secret, salt='archive-summary-v1')
archive_delete_signer = URLSafeTimedSerializer(summary_secret, salt='archive-delete-v1')
archive_edit_signer = URLSafeTimedSerializer(summary_secret, salt='archive-edit-v1')
SUMMARY_MAX_AGE = 8 * 60 * 60


@app.context_processor
def inject_globals():
    """Expose AI availability to all templates."""
    return {"ai_enabled": AIService.is_configured()}


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


_LOCAL_SETTINGS_HOSTS = {'127.0.0.1', 'localhost', '::1'}


def _valid_api_url(value):
    try:
        parts = urlsplit(value)
        _ = parts.port
        return bool(
            parts.hostname
            and (parts.scheme == 'https' or (parts.scheme == 'http' and parts.hostname in _LOCAL_SETTINGS_HOSTS))
            and parts.username is None and parts.password is None
            and not parts.query and not parts.fragment
            and not any(char.isspace() or ord(char) < 32 for char in value)
            and chr(92) not in value
        )
    except ValueError:
        return False


@app.route("/settings", methods=["GET", "POST"])
def settings():
    try:
        local_host = urlsplit(f"//{request.host}").hostname in _LOCAL_SETTINGS_HOSTS
    except ValueError:
        local_host = False
    if not local_host or request.remote_addr not in {'127.0.0.1', '::1'}:
        abort(403)

    active = AIService.settings()
    csrf_token = session.get('settings_csrf')
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        session['settings_csrf'] = csrf_token
    base_url, model = active['base_url'], active['model']
    error, status = None, 200
    if request.method == "POST":
        if not secrets.compare_digest(request.form.get('csrf_token', '').encode(), csrf_token.encode()):
            abort(403)
        base_url = request.form.get('base_url', '').strip()
        model = request.form.get('model', '').strip()
        api_key = request.form.get('api_key', '').strip()
        if len(base_url) > 2048 or not _valid_api_url(base_url):
            error = 'آدرس پایهٔ سرویس را با HTTPS وارد کنید. برای سرویس روی همین دستگاه HTTP هم پذیرفته می‌شود.'
        elif not model or len(model) > 200 or any(char.isspace() for char in model):
            error = 'شناسهٔ مدل را بدون فاصله وارد کنید.'
        elif len(api_key) > 2048 or any(char.isspace() or ord(char) < 33 or ord(char) > 126 for char in api_key) or api_key.lower() == 'your_api_key_here':
            error = 'کلید API را با حروف و نشانه‌های انگلیسی و بدون فاصله وارد کنید.'
        elif not api_key and not active['api_key']:
            error = 'کلید API را وارد کنید.'
        if error is None:
            save_ai_settings(api_key, base_url.rstrip('/'), model)
            return redirect(url_for('settings', saved=1), code=303)
        status = 400

    response = make_response(render_template(
        'settings.html', base_url=base_url, model=model, has_key=bool(active['api_key']),
        csrf_token=csrf_token, error=error, saved=request.args.get('saved') == '1',
    ), status)
    response.headers['Cache-Control'] = 'no-store'
    return response


def _calculate_natal(name, date, time, place, solar_city, vision, *, saved=None):
    if not AstroCalculator.is_available():
        raise RuntimeError("Swiss Ephemeris در دسترس نیست.")
    coordinates = (saved['latitude'], saved['longitude']) if saved else None
    birth = AstroCalculator.prepare_birth_data(date, time, place, coordinates=coordinates)
    birth.update(name=name, vision=vision, jalali_date=date, local_time=time, solar_city=solar_city or place)
    result = AstroCalculator.calculate_chart(birth)
    natal = result['chart_data']
    asc = natal.get('houses', {}).get('ascendant', {})
    birth.update(
        is_diurnal=natal.get('is_diurnal', True),
        sect_fa=natal.get('sect_fa', ''),
        asc_sign_fa=asc.get('sign_fa', ''),
        asc_sign_symbol=get_sign_symbol(asc.get('sign_fa', '')),
    )
    return {
        'birth': birth, 'natal': natal, 'solar': result['solar_return_data'],
        'id': (saved['summary_key'] if saved else None) or secrets.token_hex(16),
        'chart_id': saved['id'] if saved else None,
        'revision': saved['revision'] if saved else 0,
    }, result['html']


def _calculate_saved_natal(saved):
    return _calculate_natal(
        saved['name'], saved['birth_date_persian'], saved['birth_time_local'], saved['city_name'],
        saved['solar_city'], saved['vision'] or '', saved=saved,
    )


def _render_calculation(chart, astro_html, *, saved=False):
    birth = chart['birth']
    return render_template(
        'calculation.html', name=birth['name'], astro_data=astro_html, birth_data=birth,
        interpretation_guide=render_interpretation_guide_html(),
        summary_snapshot=summary_chart_signer.dumps(chart), saved=saved,
    )


@app.post("/calculate")
def calculate():
    """Calculate Swiss Ephemeris data and show results."""
    try:
        validated = InputValidator.validate_all(
            *(request.form.get(field, '').strip() for field in ('name', 'date', 'time', 'place', 'vision'))
        )
        chart, html = _calculate_natal(
            validated['name'], validated['date'], validated['time'], validated['place'],
            request.form.get('solar_city', '').strip(), validated['vision'],
        )
        return _render_calculation(chart, html)
    except ValidationError as exc:
        return render_template('error.html', error=str(exc))
    except Exception:
        logger.exception('Swiss Ephemeris calculation failed')
        return render_template('error.html', error='خطا در محاسبهٔ زایچه.'), 500


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
            name=safe_prompt_value(name or "مخاطب"),
            when=safe_prompt_value(prompt_when(date, time, place)),
            astro_data=safe_prompt_value(astro_data),
            vision=safe_prompt_value(vision) if vision else "تحلیل جامع زایچه، خانه به خانه",
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
            prompt_subtitle='خروجی: تفسیر خانه به خانه (۱ تا ۱۲) + سولار — متن روان، بدون HTML',
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
            name=safe_prompt_value(name or "مخاطب"),
            when=safe_prompt_value(prompt_when(date, time, place)),
            transit_data=safe_prompt_value(transit_data),
            vision=safe_prompt_value(vision) if vision else "تحلیل ترانزیت لحظه، خانه به خانه",
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
            prompt_subtitle='خروجی: ترانزیت خانه به خانه (۱ تا ۱۲) — متن روان، بدون HTML',
        )
    except Exception as e:
        logger.error(f"View transit prompt failed: {e}")
        return f"خطا در نمایش پرامپت ترانزیت: {str(e)}", 500


def _save_birth(birth, record_key, report=None):
    return save_birth_chart({
        'name': birth['name'],
        'birth_date_persian': birth['jalali_date'],
        'birth_date_gregorian': birth['gregorian_full'],
        'birth_time_local': birth['local_time'],
        'birth_time_utc': birth['utc_time'],
        'city_name': birth['city_name'],
        'latitude': birth['lat'],
        'longitude': birth['lon'],
        'timezone': birth['timezone'],
        'solar_city': birth.get('solar_city'),
        'vision': birth.get('vision', ''),
        'ai_analysis': json.dumps(report, ensure_ascii=False) if report else None,
        'summary_key': record_key,
    })


@app.post("/chart/save-birth")
def save_birth():
    try:
        chart = summary_chart_signer.loads(request.form.get('chart', ''), max_age=SUMMARY_MAX_AGE)
    except BadData:
        return _render_summary(error='اطلاعات صفحه معتبر نیست یا منقضی شده است. زایچه را دوباره محاسبه کنید.'), 400
    try:
        chart_id = chart.get('chart_id') or _save_birth(chart['birth'], chart['id'])
    except Exception:
        logger.exception('Could not save birth details')
        return render_template('error.html', error='ذخیرهٔ اطلاعات تولد ناموفق بود.'), 500
    return redirect(url_for('calculate_saved_chart', chart_id=chart_id, saved=1), code=303)


def _render_summary(birth=None, report=None, draft=None, saved_id=None, error=None):
    return render_template(
        'chart_summary.html', birth=birth, report=report, draft=draft,
        saved_id=saved_id, error=error, section_titles=SUMMARY_SECTIONS,
        analysis_html=format_analysis_html(report.get('analysis')) if report else '',
    )


@app.post("/summary")
def summarize_chart():
    try:
        chart = summary_chart_signer.loads(request.form.get('chart', ''), max_age=SUMMARY_MAX_AGE)
    except BadData:
        return _render_summary(error='اطلاعات صفحه معتبر نیست یا منقضی شده است. زایچه را دوباره محاسبه کنید.'), 400

    birth = chart['birth']
    if not AIService.is_configured():
        return _render_summary(birth=birth, error='برای تهیهٔ جمع‌بندی، کلید API را در منوی تنظیمات وارد کنید.'), 503
    try:
        report = generate_chart_summary(ai_service, chart)
        draft = summary_draft_signer.dumps({
            'id': chart.get('id') or secrets.token_hex(16), 'chart_id': chart.get('chart_id'),
            'birth': birth, 'report': report, 'revision': chart.get('revision', 0),
        })
        return _render_summary(birth=birth, report=report, draft=draft)
    except AIConfigError:
        return _render_summary(birth=birth, error='کلید سرویس هوش مصنوعی تنظیم نشده است.'), 503
    except Exception:
        logger.exception('Could not generate a chart summary')
        return _render_summary(birth=birth, error='دریافت جمع‌بندی معتبر از مدل ناموفق بود. دوباره تلاش کنید.'), 502


@app.post("/summary/save")
def save_chart_summary():
    token = request.form.get('draft', '')
    try:
        draft = summary_draft_signer.loads(token, max_age=SUMMARY_MAX_AGE)
    except BadData:
        return _render_summary(error='پیش‌نویس معتبر نیست یا منقضی شده است. جمع‌بندی را دوباره تهیه کنید.'), 400

    birth = draft['birth']
    try:
        chart_id = draft.get('chart_id')
        if chart_id:
            update_birth_chart_analysis(
                chart_id, json.dumps(draft['report'], ensure_ascii=False), revision=draft.get('revision', 0),
            )
        else:
            chart_id = _save_birth(birth, draft['id'], draft['report'])
    except StaleBirthChartError:
        return _render_summary(error='مشخصات زایچه تغییر کرده است. جمع‌بندی تازه را از فهرست زایچه‌ها تهیه کنید.'), 409
    except Exception:
        logger.exception('Could not save a chart summary')
        return _render_summary(birth=birth, report=draft['report'], draft=token,
                               error='ذخیرهٔ جمع‌بندی ناموفق بود. دوباره تلاش کنید.'), 500
    return redirect(url_for('view_chart', chart_id=chart_id), code=303)


@app.route("/analyze", methods=["POST"])
def analyze():
    """Send birth-chart data to the AI and return the rendered analysis (JSON)."""
    astro_data = request.form.get("astro_data", "").strip()
    vision = request.form.get("vision", "").strip()
    name = request.form.get("name", "").strip()
    date = request.form.get("date", "").strip()
    time = request.form.get("time", "").strip()
    place = request.form.get("place", "").strip()

    if not astro_data:
        return jsonify({"success": False, "error": "داده‌ای برای تحلیل ارسال نشد."}), 400

    if not AIService.is_configured():
        return jsonify({
            "success": False,
            "code": "no_api_key",
            "error": "کلید API را در منوی تنظیمات وارد کنید.",
        })

    try:
        analysis = ai_service.analyze_birth_chart(
            astro_data, vision=vision, name=name, date=date, time=time, place=place
        )
        return jsonify({
            "success": True,
            "analysis_html": format_analysis_html(analysis),
            "analysis_text": analysis,
        })
    except AIConfigError as e:
        return jsonify({"success": False, "code": "no_api_key", "error": str(e)})
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/analyze-transit", methods=["POST"])
def analyze_transit():
    """Send transit data to the AI and return the rendered analysis (JSON)."""
    transit_data = request.form.get("transit_data", "").strip()
    vision = request.form.get("vision", "").strip()
    name = request.form.get("name", "").strip()
    date = request.form.get("date", "").strip()
    time = request.form.get("time", "").strip()
    place = request.form.get("place", "").strip()

    if not transit_data:
        return jsonify({"success": False, "error": "داده‌ای برای تحلیل ارسال نشد."}), 400

    if not AIService.is_configured():
        return jsonify({
            "success": False,
            "code": "no_api_key",
            "error": "کلید API را در منوی تنظیمات وارد کنید.",
        })

    try:
        analysis = ai_service.analyze_transit(
            transit_data, vision=vision, name=name, date=date, time=time, place=place
        )
        return jsonify({
            "success": True,
            "analysis_html": format_analysis_html(analysis),
            "analysis_text": analysis,
        })
    except AIConfigError as e:
        return jsonify({"success": False, "code": "no_api_key", "error": str(e)})
    except Exception as e:
        logger.error(f"AI transit analysis failed: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route("/save", methods=["POST"])
def save():
    """Save birth chart to database"""
    try:
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
        return render_template(
            'charts.html', charts=all_charts, sign_archive_summary=archive_summary_signer.dumps,
            sign_archive_delete=archive_delete_signer.dumps,
        )
    except Exception as e:
        logger.error(f"Error loading charts: {e}")
        return render_template("error.html", error="خطا در بارگذاری زایچه‌ها")


@app.route("/chart/<int:chart_id>/edit", methods=["GET", "POST"])
def edit_saved_chart(chart_id):
    saved = get_birth_chart(chart_id)
    if not saved:
        abort(404)
    date, time, place = (saved[key] for key in ('birth_date_persian', 'birth_time_local', 'city_name'))
    revision = saved['revision']
    error, status = None, 200
    if request.method == "POST":
        try:
            version = archive_edit_signer.loads(request.form.get('version', ''), max_age=SUMMARY_MAX_AGE)
        except BadData:
            version = None
        if version != [chart_id, revision]:
            return render_template('error.html', error='پرونده را دوباره باز کنید و ویرایش را انجام دهید.'), 409
        date, time, place = (request.form.get(field, '').strip() for field in ('date', 'time', 'place'))
        try:
            date = InputValidator.validate_persian_date(date)
            time = InputValidator.validate_time(time)
            same_city = place == saved['city_name']
            if not same_city:
                place = InputValidator.validate_place(place)
            if (date, time, place) != (saved['birth_date_persian'], saved['birth_time_local'], saved['city_name']):
                coordinates = (saved['latitude'], saved['longitude']) if same_city else None
                birth = AstroCalculator.prepare_birth_data(date, time, place, coordinates=coordinates)
                solar_city = saved['solar_city']
                birth.update(jalali_date=date, solar_city=solar_city if solar_city and solar_city != saved['city_name'] else place)
                update_birth_details(chart_id, revision, birth)
                flash('مشخصات تولد اصلاح شد.', 'chart-edited')
            return redirect(url_for('charts'), code=303)
        except ValidationError as exc:
            error, status = str(exc), 400
        except StaleBirthChartError:
            return render_template('error.html', error='پرونده تغییر کرده است. دوباره آن را برای ویرایش باز کنید.'), 409
        except Exception:
            logger.exception('Could not edit chart %s', chart_id)
            error, status = 'ذخیرهٔ تغییرات ناموفق بود.', 500

    cities = sorted(set(get_all_cities()) | {saved['city_name']})
    return render_template(
        'edit_chart.html', chart=saved, cities=cities, date=date, time=time, place=place,
        version=archive_edit_signer.dumps([chart_id, revision]), error=error,
    ), status


@app.post("/chart/<int:chart_id>/delete")
def remove_saved_chart(chart_id):
    try:
        signed_id = archive_delete_signer.loads(request.form.get('chart', ''), max_age=SUMMARY_MAX_AGE)
    except BadData:
        signed_id = None
    if signed_id != chart_id:
        return render_template('error.html', error='فهرست زایچه‌ها را دوباره باز کنید و حذف را تأیید کنید.'), 400
    if delete_birth_chart(chart_id):
        flash('زایچه حذف شد.', 'chart-deleted')
    return redirect(url_for('charts'), code=303)


@app.get("/chart/<int:chart_id>/calculate")
def calculate_saved_chart(chart_id):
    saved = get_birth_chart(chart_id)
    if not saved:
        abort(404)
    try:
        chart, html = _calculate_saved_natal(saved)
        return _render_calculation(chart, html, saved=request.args.get('saved') == '1')
    except Exception:
        logger.exception('Could not recalculate saved chart %s', chart_id)
        return render_template('error.html', error='محاسبهٔ زایچهٔ ذخیره‌شده ناموفق بود.'), 500


@app.post("/chart/<int:chart_id>/summary")
def summarize_saved_chart(chart_id):
    try:
        signed_id = archive_summary_signer.loads(request.form.get('chart', ''), max_age=SUMMARY_MAX_AGE)
    except BadData:
        signed_id = None
    if signed_id != chart_id:
        return _render_summary(error='فهرست را دوباره باز کنید و «جمع‌بندی» را بزنید.'), 400

    saved = get_birth_chart(chart_id)
    if not saved:
        abort(404)
    if saved['has_analysis']:
        return redirect(url_for('view_chart', chart_id=chart_id), code=303)
    if not AIService.is_configured():
        return _render_summary(error='برای تهیهٔ جمع‌بندی، کلید API را در منوی تنظیمات وارد کنید.'), 503
    try:
        chart, _ = _calculate_saved_natal(saved)
        report = generate_chart_summary(ai_service, chart)
        update_birth_chart_analysis(
            chart_id, json.dumps(report, ensure_ascii=False), revision=saved['revision'], only_if_missing=True,
        )
    except StaleBirthChartError:
        return _render_summary(error='مشخصات زایچه تغییر کرده است. دوباره از فهرست زایچه‌ها جمع‌بندی بگیرید.'), 409
    except AIConfigError:
        return _render_summary(error='کلید سرویس هوش مصنوعی تنظیم نشده است.'), 503
    except Exception:
        logger.exception('Could not generate or save the analysis for chart %s', chart_id)
        return _render_summary(error='تهیه یا ذخیرهٔ جمع‌بندی ناموفق بود. دوباره تلاش کنید.'), 502
    return redirect(url_for('view_chart', chart_id=chart_id), code=303)


@app.route("/chart/<int:chart_id>")
def view_chart(chart_id):
    """View a specific chart"""
    try:
        chart = get_birth_chart(chart_id)
        if not chart:
            return render_template("error.html", error="زایچه یافت نشد")
        if not chart['has_analysis']:
            return redirect(url_for('calculate_saved_chart', chart_id=chart_id))
        if chart.get('summary_key'):
            birth = {
                'name': chart['name'], 'jalali_date': chart['birth_date_persian'],
                'gregorian_full': chart['birth_date_gregorian'], 'local_time': chart['birth_time_local'],
                'utc_time': chart['birth_time_utc'], 'city_name': chart['city_name'],
                'lat': chart['latitude'], 'lon': chart['longitude'], 'timezone': chart['timezone'],
                'solar_city': chart['solar_city'], 'vision': chart['vision'],
            }
            return _render_summary(birth=birth, report=json.loads(chart['ai_analysis']), saved_id=chart_id)
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
