import logging
from html import escape
from core import DateTimeConverter, AstroEngine
from core.course_interpretation import get_full_course_placement
from core.interpretation_guide import format_planet_house_summary
from core.soltani_interpretation import soltani_house_note
from core.astro_engine import PLANET_NAMES_FA
from core.chart_renderer import PLANET_SYMBOLS
from data import get_city_info
from utils.text_formatter import format_chart_for_ai, format_transit_for_ai
from utils.geo_format import format_arc_dms_html
from core.vedic_special_states import VEDIC_STATE_SYMBOLS, format_vedic_states_cell_html, vedic_states_td_class
from core.sign_qualities import (
    SIGN_GENDER_SYMBOLS,
    SIGN_MODALITY_SYMBOLS,
    SIGN_TRAIT_HEADERS_HTML,
    format_sign_character_cell_html,
    format_sign_trait_cells_html,
)
from core.house_meanings import (
    HOUSE_TABLE_FOOTER_HTML,
    HOUSE_TABLE_HEADERS_HTML,
    format_house_name_cell_html,
    format_house_number_cell_html,
    format_house_priority_cell_html,
)
from core.sign_qualities import format_sign_ruler_cell_html
from core.chart_conditions import format_aspect_cell_html
from core.traditional_dignities import DIGNITY_FA, DIGNITY_SYMBOLS, format_dignity_cell_html

logger = logging.getLogger(__name__)

SIGN_ELEMENT_CLASS = {
    'حمل': 'zodiac-fire',
    'اسد': 'zodiac-fire',
    'قوس': 'zodiac-fire',
    'ثور': 'zodiac-earth',
    'سنبله': 'zodiac-earth',
    'جدی': 'zodiac-earth',
    'جوزا': 'zodiac-air',
    'میزان': 'zodiac-air',
    'دلو': 'zodiac-air',
    'سرطان': 'zodiac-water',
    'عقرب': 'zodiac-water',
    'حوت': 'zodiac-water',
}


def format_sign_cell_html(sign_fa: str) -> str:
    """Zodiac sign table cell with element-based background color."""
    if not sign_fa or sign_fa == '—':
        return '<td>—</td>'
    element_class = SIGN_ELEMENT_CLASS.get(sign_fa, '')
    if element_class:
        return f'<td class="zodiac-sign-cell {element_class}">{sign_fa}</td>'
    return f'<td class="zodiac-sign-cell">{sign_fa}</td>'


RULER_COLUMNS = (
    ('triplicity_ruler', '△۱', 'صاحب مثلثه'),
    ('triplicity_ruler_2', '△۲', 'صاحب مثلثه ۲'),
    ('triplicity_participating', '△+', 'شریک مثلثه'),
    ('term_ruler', '⟦·⟧', 'صاحب حد'),
    ('face_ruler', '◩', 'صاحب وجه'),
)


DIRECT_MOTION = ('→', 'مستقیم')
RETROGRADE_MOTION = ('℞', 'راجعه')


def _format_ruler_cell(data: dict, field: str) -> str:
    planet = data.get(field)
    name = data.get(f'{field}_fa') or PLANET_NAMES_FA.get(planet, '—')
    symbol = PLANET_SYMBOLS.get(planet)
    if not symbol:
        return f'<td class="ruler-column">{escape(name)}</td>'
    label = escape(name)
    return (
        f'<td class="ruler-column"><span class="table-glyph" role="img" '
        f'aria-label="{label}" title="{label}">{symbol}</span></td>'
    )


def _minor_dignity_and_status_cells(data: dict) -> str:
    """Triplicity, term, face, essential dignity, and motion status cells."""
    dignity_cell = format_dignity_cell_html(data.get('dignity'), data.get('dignity_fa', ''))

    retrograde = data.get('retrograde')
    motion_symbol, motion_label = RETROGRADE_MOTION if retrograde else DIRECT_MOTION
    motion_class = 'table-glyph motion-retrograde' if retrograde else 'table-glyph'
    motion = (
        f'<span class="{motion_class}" role="img" aria-label="{motion_label}" '
        f'title="{motion_label}">{motion_symbol}</span>'
    )
    ruler_cells = ''.join(_format_ruler_cell(data, field) for field, _, _ in RULER_COLUMNS)
    return (
        f"{ruler_cells}"
        f"{dignity_cell}"
        f"<td>{data.get('sun_relation_fa', '—')}</td>"
        f'<td class="compact-symbol-column">{motion}</td>'
    )


def _chart_point_table_headers(name_column: str = 'سیاره') -> str:
    ruler_headers = ''.join(
        f'<th scope="col" class="ruler-column" aria-label="{label}" title="{label}">'
        f'<bdi dir="ltr">{symbol}</bdi></th>'
        for _, symbol, label in RULER_COLUMNS
    )
    return (
        f"<thead><tr><th>{name_column}</th><th>نماد</th><th>درجه در برج اعتدالی</th><th>برج</th>"
        '<th scope="col" class="compact-text-heading">حالت برج</th>'
        '<th scope="col" class="compact-symbol-column" title="جنسیت برج" aria-label="جنسیت برج">'
        '<bdi dir="ltr">♂♀</bdi></th>'
        f"<th>خانه</th>{ruler_headers}"
        '<th scope="col" class="compact-text-heading">کرامت</th><th>وضعیت شمس</th>'
        '<th scope="col" class="compact-symbol-column" title="وضعیت حرکت" aria-label="وضعیت حرکت">↔</th>'
        "<th>درجه در برج ـ سایدریل</th><th>برج ـ سایدریل</th>"
        '<th scope="col" class="compact-symbol-column" title="حالت‌های ودایی" aria-label="حالت‌های ودایی">✧</th></tr></thead><tbody>'
    )


def _format_planet_house_cell(planet_key: str | None, name_fa: str, house: int | str) -> str:
    if not planet_key or not isinstance(house, int) or not 1 <= house <= 12:
        return f'<td>{house}</td>'

    title = escape(f'{name_fa} در خانهٔ {house}')
    placement = get_full_course_placement(planet_key, house)
    if placement:
        content = (
            '<article class="course-placement-text">'
            f'<h3>{escape(placement["title"])}</h3>'
            f'{placement["html"]}</article>'
            '<details class="interp-course-placement"><summary>نکتهٔ تکمیلی</summary>'
            f'<p>{escape(soltani_house_note(name_fa, house))}</p></details>'
        )
    else:
        summary = format_planet_house_summary(name_fa, house)
        content = ''.join(f'<p>{escape(line)}</p>' for line in summary.splitlines())
    return (
        f'<td><a class="planet-house-link" href="#planetHouseModal" aria-haspopup="dialog" '
        f'aria-label="{title}">{house}</a><template>{content}</template></td>'
    )


def _format_chart_point_row(
    name_fa: str,
    symbol: str,
    data: dict,
    *,
    extra_cells: str = '',
    planet_key: str | None = None,
    symbol_font_size: str = '18px',
) -> str:
    """Build one table row for a planet or lunar node with shared column layout."""
    house_cell = _format_planet_house_cell(planet_key, name_fa, data.get('house', '—'))
    vedic_state_list = data.get('vedic_states') or []
    vedic_td_class = vedic_states_td_class(vedic_state_list)
    vedic_cell_html = format_vedic_states_cell_html(vedic_state_list)
    return (
        f"<tr><td>{name_fa}</td><td style='font-size:{symbol_font_size}'>{symbol}</td>"
        f"<td>{format_arc_dms_html(data['degree_in_sign'])}</td>"
        f"{format_sign_cell_html(data['sign_fa'])}"
        f"{format_sign_trait_cells_html(data['sign_fa'], compact_traits=True)}"
        f"{house_cell}"
        f"{extra_cells}"
        f"<td>{format_arc_dms_html(data['degree_in_sign_sidereal'])}</td>"
        f"<td>{data.get('sign_fa_sidereal', '—')}</td>"
        f"<td class='{vedic_td_class} compact-symbol-column'>{vedic_cell_html}</td></tr>"
    )


try:
    import swisseph as swe
    SWISS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Swiss Ephemeris not available: {e}")
    SWISS_AVAILABLE = False

# Initialize astro engine
if SWISS_AVAILABLE:
    astro_engine = AstroEngine()
else:
    astro_engine = None


class AstroCalculator:
    """Handles astronomical calculations using Swiss Ephemeris"""
    
    @staticmethod
    def is_available():
        """Check if Swiss Ephemeris is available"""
        return SWISS_AVAILABLE and astro_engine is not None
    
    @staticmethod
    def prepare_birth_data(persian_date, local_time, city_name, *, coordinates=None):
        """
        Convert Persian date and local time to Gregorian UTC
        
        Args:
            persian_date: String in format YYYY-MM-DD (e.g., "1400-05-12")
            local_time: String in format HH:MM (e.g., "14:30")
            city_name: Persian city name (e.g., "تهران")
            coordinates: Stored latitude and longitude when recalculating a saved chart
            
        Returns:
            Dictionary with gregorian date, UTC time, coordinates, and Julian Day
        """
        if not SWISS_AVAILABLE:
            raise RuntimeError("Swiss Ephemeris is not available")
        
        try:
            city_info = get_city_info(city_name)
            if coordinates is None:
                if not city_info:
                    raise ValueError(f"شهر '{city_name}' در دیتابیس یافت نشد")
                coordinates = city_info['lat'], city_info['lon']
            lat, lon = coordinates
            name_en = city_info.get('name_en') if city_info else None
            
            # Use DateTimeConverter for accurate conversion
            dt_data = DateTimeConverter.parse_and_convert(persian_date, local_time)
            
            return {
                "year": dt_data['utc_datetime'].year,
                "month": dt_data['utc_datetime'].month,
                "day": dt_data['utc_datetime'].day,
                "hour": dt_data['utc_datetime'].hour,
                "minute": dt_data['utc_datetime'].minute,
                "lat": lat,
                "lon": lon,
                "gregorian": dt_data['gregorian_str'],
                "gregorian_full": dt_data['gregorian_str'],
                "timezone": dt_data['timezone'],
                "location_name": f"{city_name} ({name_en})" if name_en else city_name,
                "local_time": local_time,
                "utc_time": dt_data['utc_time'],
                "julian_day": dt_data['julian_day'],
                "city_name": city_name
            }
            
        except Exception as e:
            logger.error(f"Error preparing birth data: {e}")
            raise
    
    @staticmethod
    def calculate_chart(birth_data):
        """
        Calculate astrological chart using Swiss Ephemeris
        
        Args:
            birth_data: Dictionary from prepare_birth_data()
            
        Returns:
            Dictionary with complete chart data and HTML visualization
        """
        if not SWISS_AVAILABLE or not astro_engine:
            raise RuntimeError("Swiss Ephemeris is not available")
        
        try:
            # Get Julian Day from birth_data
            jd = birth_data['julian_day']
            lat = birth_data['lat']
            lon = birth_data['lon']
            
            # Calculate complete chart using AstroEngine
            chart_data = astro_engine.calculate_complete_chart(jd, lat, lon, 'P')
            
            from datetime import datetime
            now = datetime.now()

            # Calculate Solar Return if solar_city is provided
            solar_return_data = None
            solar_city = birth_data.get('solar_city', '').strip()
            
            logger.info(f"Solar city from birth_data: '{solar_city}'")
            logger.info(f"Birth city: '{birth_data.get('city_name', '')}'")
            
            # Always calculate solar return (use birth city if solar_city not specified)
            if solar_city:
                solar_location = solar_city
            else:
                solar_location = birth_data.get('city_name', '')
            
            logger.info(f"Solar location selected: '{solar_location}'")
            
            if solar_location:
                try:
                    # Get coordinates for solar city (already imported at top)
                    solar_city_info = (
                        {'lat': lat, 'lon': lon} if solar_location == birth_data.get('city_name')
                        else get_city_info(solar_location)
                    )
                    
                    if solar_city_info:
                        # Extract birth date components
                        birth_date_parts = birth_data['gregorian_full'].split('-')
                        birth_year = int(birth_date_parts[0])
                        birth_month = int(birth_date_parts[1])
                        birth_day = int(birth_date_parts[2])
                        
                        # Calculate solar return for current year
                        solar_return_data = astro_engine.calculate_solar_return(
                            jd,
                            birth_month,
                            birth_day,
                            now.year,
                            solar_city_info['lat'],
                            solar_city_info['lon']
                        )
                        
                        if solar_return_data:
                            solar_return_data['city'] = solar_location
                            solar_return_data['city_fa'] = solar_location
                            solar_return_data['year'] = now.year
                            logger.info(f"Solar return calculated for {solar_location}")
                        else:
                            logger.warning("Solar return calculation returned None")
                    else:
                        logger.warning(f"Could not find city info for {solar_location}")
                    
                except Exception as e:
                    logger.error(f"Error calculating solar return: {e}", exc_info=True)
                    solar_return_data = None
            
            chart_html = AstroCalculator._format_chart_html(chart_data, solar_return_data)
            text_for_ai = format_chart_for_ai(chart_data, birth_data, solar_return_data)
            
            # Return both HTML version (for display) and text version (for AI)
            return {
                'html': chart_html,
                'html_for_ai': text_for_ai,  # Now returns clean text instead of HTML
                'solar_return_data': solar_return_data,
                'chart_data': chart_data,
                'birth_data': birth_data
            }
            
        except Exception as e:
            logger.error(f"Error calculating chart: {e}")
            raise

    @staticmethod
    def calculate_transit(birth_data):
        """Calculate full moment transits against natal chart."""
        if not SWISS_AVAILABLE or not astro_engine:
            raise RuntimeError("Swiss Ephemeris is not available")

        try:
            from datetime import datetime
            import jdatetime

            jd = birth_data['julian_day']
            lat = birth_data['lat']
            lon = birth_data['lon']
            chart_data = astro_engine.calculate_complete_chart(jd, lat, lon, 'P')

            now = datetime.now()
            jnow = jdatetime.datetime.now()
            jd_now = swe.julday(
                now.year, now.month, now.day,
                now.hour + now.minute / 60.0 + now.second / 3600.0,
            )
            current_date_info = {
                'gregorian': now.strftime('%Y-%m-%d %H:%M'),
                'jalali': jnow.strftime('%Y-%m-%d'),
                'jalali_full': f"{jnow.year}/{jnow.month}/{jnow.day}",
                'time_local': now.strftime('%H:%M'),
            }

            transits_data = astro_engine.calculate_full_transits(jd_now, chart_data['houses'])
            transit_aspects = astro_engine.calculate_transit_to_natal_aspects(jd_now, chart_data)

            html = AstroCalculator._format_transit_html(
                chart_data, birth_data, transits_data, transit_aspects, current_date_info,
            )
            text_for_ai = format_transit_for_ai(
                chart_data, birth_data, transits_data, transit_aspects, current_date_info,
            )

            return {
                'html': html,
                'html_for_ai': text_for_ai,
                'chart_data': chart_data,
                'birth_data': birth_data,
                'transits_data': transits_data,
                'transit_aspects': transit_aspects,
                'current_date_info': current_date_info,
            }
        except Exception as e:
            logger.error(f"Error calculating transits: {e}")
            raise

    @staticmethod
    def _format_solar_return_html(solar_return_data) -> str:
        """Solar return section — yearly forecast from birthday in current year."""
        if not solar_return_data:
            return ''

        year = solar_return_data.get('year')
        year_label = f' · {year}' if year else ''
        city = escape(solar_return_data.get('city_fa') or 'نامشخص')
        html = (
            "<section class='solar-return' aria-labelledby='solarReturnTitle'>"
            "<header class='solar-return__header'>"
            f"<h2 id='solarReturnTitle'>بازگشت خورشید{year_label}</h2>"
            f"<p>شهر سالگرد: {city}</p></header>"
        )

        html += "<h4 style='color:#2c3e50; margin-top:15px;'>زوایای اصلی سولار:</h4>"
        html += "<table class='astro-table'>"
        html += (
            "<thead><tr><th>زاویه</th><th>درجه کل</th><th>درجه در برج</th><th>برج</th>"
            f"{SIGN_TRAIT_HEADERS_HTML}</tr></thead><tbody>"
        )
        asc = solar_return_data['angles']['asc']
        mc = solar_return_data['angles']['mc']
        html += (
            f"<tr><td>طالع سولار (ASC)</td>"
            f"<td>{format_arc_dms_html(asc['longitude'])}</td>"
            f"<td>{format_arc_dms_html(asc['degree_in_sign'])}</td>"
            f"{format_sign_cell_html(asc['sign_fa'])}"
            f"{format_sign_trait_cells_html(asc['sign_fa'])}</tr>"
        )
        html += (
            f"<tr><td>قله آسمان سولار (MC)</td>"
            f"<td>{format_arc_dms_html(mc['longitude'])}</td>"
            f"<td>{format_arc_dms_html(mc['degree_in_sign'])}</td>"
            f"{format_sign_cell_html(mc['sign_fa'])}"
            f"{format_sign_trait_cells_html(mc['sign_fa'])}</tr>"
        )
        html += "</tbody></table>"

        html += "<h4 style='color:#2c3e50; margin-top:15px;'>کواکب در چارت سولار:</h4>"
        html += "<table class='astro-table'>"
        html += (
            "<thead><tr><th>سیاره</th><th>درجه کل</th><th>درجه در برج</th><th>برج</th>"
            f"{SIGN_TRAIT_HEADERS_HTML}</tr></thead><tbody>"
        )
        for name, data in solar_return_data['planets'].items():
            html += (
                f"<tr><td>{data['name_fa']}</td>"
                f"<td>{format_arc_dms_html(data['longitude'])}</td>"
                f"<td>{format_arc_dms_html(data['degree_in_sign'])}</td>"
                f"{format_sign_cell_html(data['sign_fa'])}"
                f"{format_sign_trait_cells_html(data['sign_fa'])}</tr>"
            )
        html += "</tbody></table>"
        return html + "</section>"

    @staticmethod
    def _format_transit_planet_rows(transit_group: dict) -> str:
        rows = ''
        for _name, data in transit_group.items():
            if not data:
                continue
            retro = "<span style='color:red'>راجعه ℞</span>" if data['retrograde'] else "مستقیم"
            rows += (
                f"<tr><td>{data['name_fa']}</td>"
                f"<td>{format_arc_dms_html(data['longitude'])}</td>"
                f"<td>{format_arc_dms_html(data['degree_in_sign'])}</td>"
                f"{format_sign_cell_html(data['sign_fa'])}"
                f"{format_sign_trait_cells_html(data['sign_fa'])}"
                f"<td>خانه {data['natal_house']}</td><td>{retro}</td></tr>"
            )
        return rows

    @staticmethod
    def _format_transit_html(chart_data, birth_data, transits_data, transit_aspects, current_date_info):
        """Format full transit page HTML."""
        html = (
            "<div class='section-title'>🌍 ترانزیت لحظه — موقعیت آسمان در برابر زایچه تولد</div>"
            f"<p style='text-align:center; color:#666; font-size:12px;'>"
            f"تاریخ و ساعت محاسبه: {current_date_info['jalali_full']} شمسی "
            f"({current_date_info['gregorian']} به وقت محلی)</p>"
        )

        html += "<h4 style='color:#2c3e50; margin-top:12px;'>سیارات کند</h4>"
        html += "<table class='astro-table'>"
        html += (
            "<tr><th>سیاره</th><th>درجه کل</th><th>درجه در برج</th><th>برج</th>"
            f"{SIGN_TRAIT_HEADERS_HTML}"
            "<th>خانهٔ تولد</th><th>وضعیت</th></tr>"
        )
        html += AstroCalculator._format_transit_planet_rows(transits_data.get('slow', {}))
        html += "</table>"

        html += "<h4 style='color:#2c3e50; margin-top:15px;'>سیارات شخصی (سریع)</h4>"
        html += "<table class='astro-table'>"
        html += (
            "<tr><th>سیاره</th><th>درجه کل</th><th>درجه در برج</th><th>برج</th>"
            f"{SIGN_TRAIT_HEADERS_HTML}"
            "<th>خانهٔ تولد</th><th>وضعیت</th></tr>"
        )
        html += AstroCalculator._format_transit_planet_rows(transits_data.get('fast', {}))
        html += "</table>"

        nodes = transits_data.get('nodes') or {}
        if nodes:
            html += "<h4 style='color:#2c3e50; margin-top:15px;'>عقده‌های قمری (ترانزیت)</h4>"
            html += "<table class='astro-table'>"
            html += (
                "<tr><th>عقده</th><th>درجه کل</th><th>درجه در برج</th><th>برج</th>"
                f"{SIGN_TRAIT_HEADERS_HTML}"
                "<th>خانهٔ تولد</th><th>وضعیت</th></tr>"
            )
            html += AstroCalculator._format_transit_planet_rows(nodes)
            html += "</table>"

        if transit_aspects:
            html += "<div class='section-title'>⚹ اتصالات ترانزیت به زایچه تولد</div>"
            html += "<table class='astro-table aspects-table'>"
            html += (
                "<tr><th>فاعل → قابل</th><th>اتصال</th><th>طبع</th>"
                "<th>فاز</th><th>زاویه</th><th>تقریب</th></tr>"
            )
            for aspect in transit_aspects[:30]:
                exact_mark = " ⭐" if aspect['exact'] else ""
                html += (
                    f"<tr><td>{aspect.get('caster_receiver_fa', '—')}</td>"
                    f"{format_aspect_cell_html(aspect['aspect'], aspect['aspect_fa'], aspect['symbol'])}"
                    f"<td>{aspect.get('nature_fa', '—')}</td>"
                    f"<td>{aspect.get('phase_fa', '—')}</td>"
                    f"<td>{format_arc_dms_html(aspect['angle'])}</td>"
                    f"<td>{format_arc_dms_html(aspect['orb'])}{exact_mark}</td></tr>"
                )
            html += "</table>"

        html += (
            "<p class='astro-methodology-note'>"
            "ترانزیت: موقعیت فعلی آسمان روی خانه‌های زایچه تولد؛ "
            "سیارات کند تم‌های بلندمدت، سیارات سریع رویدادهای کوتاه‌مدت را نشان می‌دهند."
            "</p>"
        )
        return html

    @staticmethod
    def _format_chart_html(chart_data, solar_return_data):
        """Format natal chart data as HTML (no transits)."""
        html = "<div class='section-title'>🏠 خانه‌ها (پلاسیدیوس)</div>"
        html += "<table class='astro-table houses-table'>"
        html += HOUSE_TABLE_HEADERS_HTML

        for house in chart_data['houses']['cusps']:
            html += (
                f"<tr>{format_house_number_cell_html(house['house'])}"
                f"{format_house_name_cell_html(house['house'])}"
                f"{format_house_priority_cell_html(house['house'])}"
                f"<td>{format_arc_dms_html(house['degree_in_sign'])}</td>"
                f"{format_sign_cell_html(house['sign_fa'])}"
                f"{format_sign_ruler_cell_html(house['sign_fa'])}"
                f"{format_sign_trait_cells_html(house['sign_fa'])}"
                f"{format_sign_character_cell_html(house['sign_fa'], extra_class='houses-group-end')}</tr>"
            )

        html += HOUSE_TABLE_FOOTER_HTML + "</table>"

        html += "<div class='section-title' id='natal-planets-title'>🪐 کواکب</div>"
        ruler_key = ' · '.join(
            f'<bdi dir="ltr">{symbol}</bdi> {label}' for _, symbol, label in RULER_COLUMNS
        )
        gender_key = ' · '.join(f'{symbol} {label}' for label, symbol in SIGN_GENDER_SYMBOLS.items())
        motion_key = ' · '.join(f'{symbol} {label}' for symbol, label in (DIRECT_MOTION, RETROGRADE_MOTION))
        modality_key = ' · '.join(f'{symbol} {label}' for label, symbol in SIGN_MODALITY_SYMBOLS.items())
        vedic_key = ' · '.join(f'{symbol} {label}' for label, symbol in VEDIC_STATE_SYMBOLS.items())
        dignity_key = ' · '.join(
            f'<bdi dir="ltr">{symbol}</bdi> {DIGNITY_FA[key]}' for key, symbol in DIGNITY_SYMBOLS.items()
        )
        html += (
            "<details class='ruler-symbol-key'><summary>راهنمای نماد ستون‌ها</summary>"
            f"<p>{ruler_key}</p><p>جنسیت برج: {gender_key} | وضعیت حرکت: {motion_key}</p>"
            f"<p>حالت برج: {modality_key}</p><p>حالت‌های ودایی: {vedic_key}</p>"
            f"<p>کرامت: {dignity_key}</p></details>"
        )
        html += (
            "<div class='chart-point-scroll' role='region' tabindex='0' aria-labelledby='natal-planets-title'>"
            "<table class='astro-table'>"
        )
        html += _chart_point_table_headers('سیاره')

        for name, data in chart_data['planets'].items():
            if data:
                symbol = PLANET_SYMBOLS.get(name, '')
                html += _format_chart_point_row(
                    data['name_fa'],
                    symbol,
                    data,
                    extra_cells=_minor_dignity_and_status_cells(data),
                    planet_key=name,
                )

        html += "</tbody></table></div>"

        if chart_data.get('nodes'):
            html += "<div class='section-title' id='natal-nodes-title'>🌙 عقده‌های قمری</div>"
            html += (
                "<div class='chart-point-scroll' role='region' tabindex='0' aria-labelledby='natal-nodes-title'>"
                "<table class='astro-table'>"
            )
            html += _chart_point_table_headers('نام')

            nn = chart_data['nodes']['north_node']
            sn = chart_data['nodes']['south_node']

            html += _format_chart_point_row(
                nn['name_fa'], '☊', nn, extra_cells=_minor_dignity_and_status_cells(nn)
            )
            html += _format_chart_point_row(
                sn['name_fa'], '☋', sn, extra_cells=_minor_dignity_and_status_cells(sn)
            )
            html += "</tbody></table></div>"

        # Add aspects
        if chart_data.get('aspects'):
            html += "<div class='section-title'>⚹ اتصالات به نظر</div>"
            html += "<table class='astro-table aspects-table'>"
            html += (
                "<thead><tr><th>فاعل → قابل</th><th>اتصال</th><th>طبع</th>"
                "<th>فاز</th><th>زاویه</th><th>تقریب</th></tr></thead><tbody>"
            )

            for aspect in chart_data['aspects'][:20]:
                exact_mark = " ⭐" if aspect['exact'] else ""
                html += (
                    f"<tr><td>{aspect.get('caster_receiver_fa', '—')}</td>"
                    f"{format_aspect_cell_html(aspect['aspect'], aspect['aspect_fa'], aspect['symbol'])}"
                    f"<td>{aspect.get('nature_fa', '—')}</td>"
                    f"<td>{aspect.get('phase_fa', '—')}</td>"
                    f"<td>{format_arc_dms_html(aspect['angle'])}</td>"
                    f"<td>{format_arc_dms_html(aspect['orb'])}{exact_mark}</td></tr>"
                )

            html += "</tbody></table>"
            html += (
                "<p style='text-align:center; color:#888; font-size:11px; margin-top:8px;'>"
                "⭐ اتصال دقیق (تقریب &lt; ۱°)؛ ملاقاتی = نزدیک‌شونده، انفصالی = دورشونده؛ "
                "فاعل = کوکب سریع‌تر، قابل = کندتر. "
                "رنگ ستون اتصال: سبز = سعد، قرمز = نحس، بنفش = متغیر؛ "
                "شدت رنگ متناسب قدرت نظر (اقتران ۱۰۰٪، مقابله ۵۰٪، …)."
                "</p>"
            )

        local_aspects = chart_data.get('local_aspects')
        if local_aspects is not None:
            html += "<div class='section-title'>اتصالات به محل</div>"
            html += (
                "<p class='astro-methodology-note'>اتفاق قوت: تقارن نسبت به محور حمل–میزان؛ "
                "اتفاق طریقت: تقارن نسبت به محور سرطان–جدی. "
                "معیار نمایش: فاصلهٔ طول‌های اعتدالی تا تقارن کمتر از ۱° است.</p>"
            )
            if local_aspects:
                html += (
                    "<table class='astro-table local-aspects-table'>"
                    "<thead><tr><th>دو نقطه</th><th>نوع اتصال</th><th>فاز</th><th>فاصله تا تقارن</th></tr></thead><tbody>"
                )
                for aspect in local_aspects:
                    # Keep the displayed arc below one degree, even near the cutoff.
                    minutes, seconds = divmod(int(aspect['orb'] * 3600), 60)
                    approximation = f'<span class="arc-dms">{minutes:02d}′ {seconds:02d}″</span>'
                    html += (
                        f"<tr><td>{aspect['pair_fa']}</td><td>{aspect['type_fa']}</td>"
                        f"<td>{aspect['phase_fa']}</td><td>{approximation}</td></tr>"
                    )
                html += "</tbody></table>"
            else:
                html += "<p>در لحظهٔ تولد، اتصال به محل با تقریب کمتر از ۱° یافت نشد.</p>"

        html += AstroCalculator._format_solar_return_html(solar_return_data)

        return html
