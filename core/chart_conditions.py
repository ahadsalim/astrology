"""Traditional chart conditions: solar phase for planets, aspect phase and casting."""

from __future__ import annotations

from typing import Dict, Optional

# Mean daily motion rank (lower = faster). Used when speeds are tied or missing.
PLANET_SPEED_RANK = {
    'Moon': 1,
    'Mercury': 2,
    'Venus': 3,
    'Sun': 4,
    'Mars': 5,
    'Jupiter': 6,
    'Saturn': 7,
    'Uranus': 8,
    'Neptune': 9,
    'Pluto': 10,
    'NorthNode': 11,
    'SouthNode': 11,
}

SUPERIOR_PLANETS = frozenset({'Mars', 'Jupiter', 'Saturn'})
INFERIOR_PLANETS = frozenset({'Moon', 'Mercury', 'Venus'})

ASPECT_NATURE_FA = {
    'Conjunction': 'متغیر',
    'Opposition': 'نحس',
    'Trine': 'سعد',
    'Square': 'نحس',
    'Sextile': 'سعد',
}

# Traditional relative power (aspect.txt); colors: benefic green, malefic red, variable purple.
ASPECT_SPECTRUM = {
    'Conjunction': {'power': '۱۰۰٪', 'nature': 'variable', 'bg': '#5b4a8a', 'text': '#fff'},
    'Opposition': {'power': '۵۰٪', 'nature': 'malefic', 'bg': '#4a0e0e', 'text': '#fff'},
    'Trine': {'power': '۳۳٪', 'nature': 'benefic', 'bg': '#0b5345', 'text': '#fff'},
    'Square': {'power': '۲۵٪', 'nature': 'malefic', 'bg': '#a93226', 'text': '#fff'},
    'Sextile': {'power': '۱۶٪', 'nature': 'benefic', 'bg': '#b8e6b8', 'text': '#1a4d1a'},
}

ASPECT_CSS_CLASS = {
    'Conjunction': 'aspect--conjunction',
    'Opposition': 'aspect--opposition',
    'Trine': 'aspect--trine',
    'Square': 'aspect--square',
    'Sextile': 'aspect--sextile',
}

ASPECT_PHASE_FA = {
    'applying': 'ملاقاتی',
    'separating': 'انفصالی',
    'exact': 'دقیق',
    'unknown': '—',
}


def _shortest_separation_deg(lon1: float, lon2: float) -> float:
    return abs(((lon1 - lon2 + 180) % 360) - 180)


def get_sun_relation(planet_key: str, planet_lon: float, sun_lon: float) -> Dict[str, str]:
    """
    Traditional solar distance state (aspect.txt §136–177).
    Returns keys: sun_relation, sun_relation_fa.
    """
    if planet_key in ('Sun', 'NorthNode', 'SouthNode'):
        return {'sun_relation': 'none', 'sun_relation_fa': '—'}

    sep = _shortest_separation_deg(planet_lon, sun_lon)

    if sep <= 16 / 60:
        return {'sun_relation': 'cazimi', 'sun_relation_fa': 'تصمیم'}
    if sep <= 6:
        return {'sun_relation': 'combust', 'sun_relation_fa': 'احتراق'}
    if sep <= 12:
        return {'sun_relation': 'under_beams', 'sun_relation_fa': 'تحت‌الشعاع'}

    sun_ahead = (sun_lon - planet_lon) % 360
    planet_ahead = (planet_lon - sun_lon) % 360

    if planet_key in SUPERIOR_PLANETS:
        if 15 <= sun_ahead <= 90:
            return {'sun_relation': 'oriental', 'sun_relation_fa': 'تشریق (علوی)'}
        if 90 < sun_ahead <= 180 or 15 <= planet_ahead <= 90:
            return {'sun_relation': 'occidental', 'sun_relation_fa': 'مغربی'}
        if sep <= 90:
            return {'sun_relation': 'weak_oriental', 'sun_relation_fa': 'ضعیف‌التشریق'}
        return {'sun_relation': 'free', 'sun_relation_fa': 'عادی'}

    if planet_key in INFERIOR_PLANETS:
        if planet_key == 'Mercury' and 12 < planet_ahead <= 27:
            return {'sun_relation': 'occidental_inferior', 'sun_relation_fa': 'تغریب (سفلی)'}
        if planet_key == 'Venus' and 12 < planet_ahead <= 47:
            return {'sun_relation': 'occidental_inferior', 'sun_relation_fa': 'تغریب (سفلی)'}
        if planet_key == 'Moon' and planet_ahead > 12:
            return {'sun_relation': 'occidental_inferior', 'sun_relation_fa': 'تغریب (سفلی)'}
        if 15 <= sun_ahead <= 90:
            return {'sun_relation': 'oriental', 'sun_relation_fa': 'مشرقی'}
        return {'sun_relation': 'free', 'sun_relation_fa': 'عادی'}

    if sep <= 30:
        return {'sun_relation': 'near', 'sun_relation_fa': 'نزدیک (متغیر)'}
    return {'sun_relation': 'free', 'sun_relation_fa': 'عادی'}


def _angular_distance(lon1: float, lon2: float) -> float:
    diff = abs(lon1 - lon2)
    return 360 - diff if diff > 180 else diff


def get_aspect_phase(
    lon1: float,
    lon2: float,
    speed1: float,
    speed2: float,
    target_angle: float,
) -> str:
    """Applying (ملاقاتی) vs separating (انفصالی) from short-term orb change."""
    dt = 0.05
    dist_now = _angular_distance(lon1, lon2)
    dist_future = _angular_distance(lon1 + speed1 * dt, lon2 + speed2 * dt)
    orb_now = abs(dist_now - target_angle)
    orb_future = abs(dist_future - target_angle)

    if orb_now < 0.02:
        return 'exact'
    if orb_future < orb_now - 1e-5:
        return 'applying'
    if orb_future > orb_now + 1e-5:
        return 'separating'
    return 'unknown'


def get_aspect_caster_receiver(
    point1: str,
    point2: str,
    speed1: Optional[float],
    speed2: Optional[float],
) -> Dict[str, str]:
    """Faster planet casts to slower (سریع‌رو → کندرو). Returns caster/receiver keys."""
    if speed1 is not None and speed2 is not None and speed1 != speed2:
        faster_is_1 = abs(speed1) > abs(speed2)
    else:
        rank1 = PLANET_SPEED_RANK.get(point1, 99)
        rank2 = PLANET_SPEED_RANK.get(point2, 99)
        faster_is_1 = rank1 < rank2 if rank1 != rank2 else True

    if faster_is_1:
        return {'caster': point1, 'receiver': point2}
    return {'caster': point2, 'receiver': point1}


def enrich_aspect_record(
    aspect: Dict,
    *,
    lon1: float,
    lon2: float,
    speed1: Optional[float],
    speed2: Optional[float],
    name1_fa: str,
    name2_fa: str,
    target_angle: float,
    aspect_name: str,
) -> None:
    """Attach phase, nature, and caster→receiver (Persian) to an aspect dict in place."""
    phase = get_aspect_phase(lon1, lon2, speed1 or 0.0, speed2 or 0.0, target_angle)
    aspect['phase'] = phase
    aspect['phase_fa'] = ASPECT_PHASE_FA.get(phase, '—')
    aspect['nature_fa'] = ASPECT_NATURE_FA.get(aspect_name, '—')

    casting = get_aspect_caster_receiver(aspect['planet1'], aspect['planet2'], speed1, speed2)
    aspect['caster'] = casting['caster']
    aspect['receiver'] = casting['receiver']
    names = {aspect['planet1']: name1_fa, aspect['planet2']: name2_fa}
    aspect['caster_receiver_fa'] = (
        f"{names[casting['caster']]} → {names[casting['receiver']]}"
    )


def format_aspect_cell_html(aspect_key: str, aspect_fa: str, symbol: str = '') -> str:
    """Colored aspect-type cell by traditional power rank and saad/nahs nature."""
    label = f'{aspect_fa} {symbol}'.strip()
    css = ASPECT_CSS_CLASS.get(aspect_key, '')
    colors = ASPECT_SPECTRUM.get(aspect_key)
    if not colors:
        return f'<td class="aspect-cell">{label}</td>'
    cls = f'aspect-cell {css}'.strip()
    return (
        f'<td class="{cls}" '
        f'style="background:{colors["bg"]};color:{colors["text"]};">'
        f'{label}</td>'
    )
