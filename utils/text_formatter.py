# -*- coding: utf-8 -*-
"""
Text Formatter for AI
Converts chart data to clean structured text for manual AI analysis
"""

from utils.geo_format import format_coordinates, format_arc_dms
from core.house_meanings import get_house_meaning_fa
from core.sign_qualities import get_sign_ruler_fa


PLANET_ORDER = [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
    'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
]


def _house_for_longitude(longitude, houses_data):
    """Return natal house number for an ecliptic longitude."""
    cusps = (houses_data or {}).get('cusps') or []
    if not cusps or longitude is None:
        return None
    for i, cusp in enumerate(cusps):
        current_cusp = cusp['longitude']
        next_cusp = cusps[(i + 1) % 12]['longitude']
        if next_cusp < current_cusp:
            if longitude >= current_cusp or longitude < next_cusp:
                return cusp['house']
        elif current_cusp <= longitude < next_cusp:
            return cusp['house']
    return cusps[0].get('house', 1)


def _occupants_by_house(chart_data):
    occupants = {i: [] for i in range(1, 13)}
    for data in (chart_data.get('planets') or {}).values():
        if data and data.get('house'):
            occupants[int(data['house'])].append(data['name_fa'])
    for node in (chart_data.get('nodes') or {}).values():
        if node and node.get('house'):
            occupants[int(node['house'])].append(node['name_fa'])
    return occupants


def _format_house_cusps(chart_data):
    """Plain-text natal houses with cusp, ruler, and occupants."""
    lines = []
    lines.append("🏠 خانه‌ها (پلاسیدیوس) — برای تفسیر خانه به خانه:")
    lines.append("-" * 80)
    occupants = _occupants_by_house(chart_data)
    for house in chart_data.get('houses', {}).get('cusps', []):
        num = house['house']
        names = occupants.get(num) or []
        occupant_text = "، ".join(names) if names else "خالی"
        lines.append(f"  خانه {num} ({get_house_meaning_fa(num)}):")
        lines.append(
            f"    - رأس: {format_arc_dms(house['degree_in_sign'])} {house['sign_fa']}"
            f" — حاکم برج: {get_sign_ruler_fa(house['sign_fa'])}"
        )
        lines.append(f"    - ساکنان: {occupant_text}")
    lines.append("")
    return lines


def _format_transit_body_lines(data: dict) -> list[str]:
    lines = []
    retro = " [راجعه]" if data.get('retrograde') else ""
    lines.append(f"  {data['name_fa']}:")
    lines.append(f"    - درجه کل: {format_arc_dms(data['longitude'])}")
    lines.append(f"    - درجه در برج: {format_arc_dms(data['degree_in_sign'])}")
    lines.append(f"    - برج: {data['sign_fa']}")
    lines.append(f"    - در خانه {data['natal_house']} زایچه تولد{retro}")
    return lines


def format_chart_for_ai(chart_data, birth_data, solar_return_data=None):
    """Format natal chart + solar return as plain text (no transits)."""
    lines = []
    lines.append("=" * 80)
    lines.append("اطلاعات زایچه تولد و چارت سولار")
    lines.append("=" * 80)
    lines.append("")

    lines.append("📋 اطلاعات فرد:")
    lines.append(f"  • نام: {birth_data.get('name', 'نامشخص')}")
    lines.append(f"  • تاریخ تولد (شمسی): {birth_data.get('jalali_date', 'نامشخص')}")
    lines.append(f"  • تاریخ تولد (میلادی): {birth_data.get('gregorian_full', 'نامشخص')}")
    lines.append(f"  • ساعت تولد (محلی): {birth_data.get('local_time', 'نامشخص')}")
    lines.append(f"  • محل تولد: {birth_data.get('city_name', 'نامشخص')}")
    lat = birth_data.get('lat', 0)
    lon = birth_data.get('lon', 0)
    lines.append(f"  • مختصات: {format_coordinates(lat, lon)}")
    if birth_data.get('vision'):
        lines.append(f"  • دغدغه/هدف: {birth_data['vision']}")
    if chart_data.get('is_diurnal') is not None:
        sect = 'مولود روز (سکت روز)' if chart_data['is_diurnal'] else 'مولود شب (سکت شب)'
        lines.append(f"  • بخش زایچه: {sect}")
    if chart_data.get('sect_fa'):
        lines.append(f"  • سکت: {chart_data['sect_fa']}")
    lines.append("")

    lines.append("🌟 زوایای اصلی:")
    lines.append("-" * 80)
    asc = chart_data['houses']['ascendant']
    mc = chart_data['houses']['midheaven']
    lines.append(f"  طالع (ASC):")
    lines.append(
        f"    - درجه در برج اعتدالی: {format_arc_dms(asc['degree_in_sign'])} — برج: {asc['sign_fa']}"
    )
    lines.append(f"  قله آسمان (MC):")
    lines.append(
        f"    - درجه در برج اعتدالی: {format_arc_dms(mc['degree_in_sign'])} — برج: {mc['sign_fa']}"
    )
    lines.append("")

    lines.extend(_format_house_cusps(chart_data))

    lines.append("🪐 کواکب:")
    lines.append("-" * 80)
    for name in PLANET_ORDER:
        if name in chart_data['planets']:
            data = chart_data['planets'][name]
            if data:
                lines.append(f"  {data['name_fa']}:")
                lines.append(
                    f"    - درجه در برج اعتدالی: {format_arc_dms(data['degree_in_sign'])} — برج: {data['sign_fa']}"
                )
                lines.append(f"    - خانه: {data['house']}")
                if data.get('triplicity_ruler_fa'):
                    lines.append(f"    - صاحب مثلثه: {data['triplicity_ruler_fa']}")
                if data.get('triplicity_ruler_2_fa'):
                    lines.append(f"    - صاحب مثلثه ۲: {data['triplicity_ruler_2_fa']}")
                if data.get('triplicity_participating_fa'):
                    lines.append(f"    - شریک مثلثه: {data['triplicity_participating_fa']}")
                dignity_fa = data.get('dignity_fa', '')
                if dignity_fa:
                    lines.append(f"    - کرامت: {dignity_fa}")
                if data.get('sun_relation_fa') and data['sun_relation_fa'] != '—':
                    lines.append(f"    - وضعیت شمس: {data['sun_relation_fa']}")
                lines.append(f"    - وضعیت: {'راجعه' if data['retrograde'] else 'مستقیم'}")
                lines.append("")

    nodes = chart_data.get('nodes') or {}
    if nodes:
        lines.append("☊☋ عقده‌های قمری:")
        lines.append("-" * 80)
        for key in ('north_node', 'south_node'):
            node = nodes.get(key)
            if not node:
                continue
            lines.append(f"  {node['name_fa']}:")
            lines.append(
                f"    - درجه در برج اعتدالی: {format_arc_dms(node['degree_in_sign'])} — برج: {node['sign_fa']}"
            )
            if node.get('house'):
                lines.append(f"    - خانه: {node['house']}")
            lines.append("")

    if chart_data.get('aspects'):
        lines.append("⚹ اتصالات مهم:")
        lines.append("-" * 80)
        for i, aspect in enumerate(chart_data['aspects'][:30], 1):
            exact_mark = " [دقیق]" if aspect['exact'] else ""
            caster = aspect.get('caster_receiver_fa', '')
            phase = aspect.get('phase_fa', '')
            nature = aspect.get('nature_fa', '')
            lines.append(f"  {i}. {caster or aspect['planet1_fa'] + ' ' + aspect['aspect_fa'] + ' ' + aspect['planet2_fa']}")
            extra = f" | طبع: {nature}" if nature else ""
            extra += f" | فاز: {phase}" if phase else ""
            lines.append(
                f"     زاویه: {format_arc_dms(aspect['angle'])} | تقریب: {format_arc_dms(aspect['orb'])}{exact_mark}{extra}"
            )
        lines.append("")

    if solar_return_data:
        year = solar_return_data.get('year', '')
        lines.append("🎂 پیش‌بینی سال جاری — چارت سولار (Solar Return):")
        lines.append("-" * 80)
        lines.append(
            f"  چارت لحظهٔ بازگشت خورشید به درجهٔ تولد در سالگرد تولد امسال"
            f"{f' ({year})' if year else ''}؛ تم یک سال کامل تا سالگرد بعد."
        )
        lines.append(f"  محل حضور در سالگرد: {solar_return_data.get('city_fa', 'نامشخص')}")
        lines.append("")
        asc = solar_return_data['angles']['asc']
        mc = solar_return_data['angles']['mc']
        lines.append(f"    طالع سولار: {format_arc_dms(asc['degree_in_sign'])} {asc['sign_fa']}")
        lines.append(f"    قله آسمان سولار: {format_arc_dms(mc['degree_in_sign'])} {mc['sign_fa']}")
        lines.append("")
        lines.append("  کواکب سولار (با خانهٔ فعال‌شده در زایچه تولد):")
        natal_houses = chart_data.get('houses')
        for name in PLANET_ORDER:
            if name in solar_return_data.get('planets', {}):
                data = solar_return_data['planets'][name]
                natal_house = _house_for_longitude(data.get('longitude'), natal_houses)
                house_note = f" — خانه {natal_house} زایچه تولد" if natal_house else ""
                lines.append(
                    f"    {data['name_fa']}: {format_arc_dms(data['degree_in_sign'])} {data['sign_fa']}{house_note}"
                )
        lines.append("")

    lines.append("=" * 80)
    lines.append("پایان داده‌ها")
    lines.append("=" * 80)
    return "\n".join(lines)


def format_transit_for_ai(chart_data, birth_data, transits_data, transit_aspects, current_date_info):
    """Format full transit data as plain text for manual AI analysis."""
    lines = []
    lines.append("=" * 80)
    lines.append("ترانزیت لحظه — آسمان فعلی در برابر زایچه تولد")
    lines.append("=" * 80)
    lines.append("")

    lines.append("📋 زایچه تولد (مرجع):")
    lines.append(f"  • نام: {birth_data.get('name', 'نامشخص')}")
    lines.append(f"  • تاریخ تولد (شمسی): {birth_data.get('jalali_date', 'نامشخص')}")
    lines.append(f"  • ساعت تولد: {birth_data.get('local_time', 'نامشخص')}")
    lines.append(f"  • محل تولد: {birth_data.get('city_name', 'نامشخص')}")
    asc = chart_data['houses']['ascendant']
    lines.append(f"  • طالع تولد: {asc['sign_fa']}")
    lines.append("")

    lines.append("🏠 خانه‌های زایچه تولد که الان ترانزیت دارند:")
    lines.append("-" * 80)
    by_house = {i: [] for i in range(1, 13)}
    for group_key in ('slow', 'fast', 'nodes'):
        group = transits_data.get(group_key) or {}
        for data in group.values():
            if not data:
                continue
            house_num = data.get('natal_house')
            if not house_num:
                continue
            retro = " [راجعه]" if data.get('retrograde') else ""
            by_house[int(house_num)].append(f"{data['name_fa']}{retro}")
    for num in range(1, 13):
        names = by_house[num]
        occupant_text = "، ".join(names) if names else "ساکت"
        lines.append(f"  خانه {num} ({get_house_meaning_fa(num)}): {occupant_text}")
    lines.append("")

    lines.append("🕐 زمان محاسبه ترانزیت:")
    lines.append(f"  • شمسی: {current_date_info['jalali_full']}")
    lines.append(f"  • میلادی: {current_date_info['gregorian']}")
    lines.append("")

    lines.append("🐢 سیارات کند (ترانزیت):")
    lines.append("-" * 80)
    for _name, data in transits_data.get('slow', {}).items():
        if data:
            lines.extend(_format_transit_body_lines(data))
            lines.append("")
    lines.append("")

    lines.append("⚡ سیارات شخصی (ترانزیت):")
    lines.append("-" * 80)
    for _name, data in transits_data.get('fast', {}).items():
        if data:
            lines.extend(_format_transit_body_lines(data))
            lines.append("")
    lines.append("")

    nodes = transits_data.get('nodes') or {}
    if nodes:
        lines.append("☊☋ عقده‌های قمری (ترانزیت):")
        lines.append("-" * 80)
        for _key, data in nodes.items():
            if data:
                lines.extend(_format_transit_body_lines(data))
                lines.append("")
        lines.append("")

    if transit_aspects:
        lines.append("⚹ اتصالات ترانزیت به زایچه تولد:")
        lines.append("-" * 80)
        for i, aspect in enumerate(transit_aspects[:30], 1):
            exact_mark = " [دقیق]" if aspect['exact'] else ""
            caster = aspect.get('caster_receiver_fa', '')
            phase = aspect.get('phase_fa', '')
            nature = aspect.get('nature_fa', '')
            lines.append(f"  {i}. {caster or aspect['planet1_fa'] + ' ' + aspect['aspect_fa'] + ' ' + aspect['planet2_fa']}")
            extra = f" | طبع: {nature}" if nature else ""
            extra += f" | فاز: {phase}" if phase else ""
            lines.append(
                f"     زاویه: {format_arc_dms(aspect['angle'])} | تقریب: {format_arc_dms(aspect['orb'])}{exact_mark}{extra}"
            )
        lines.append("")

    lines.append("=" * 80)
    lines.append("پایان داده‌های ترانزیت")
    lines.append("=" * 80)
    return "\n".join(lines)
