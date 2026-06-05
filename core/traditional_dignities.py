# -*- coding: utf-8 -*-
"""
Traditional minor essential dignities: triplicity, terms (bounds), and faces (decans).
Swiss Ephemeris does not provide these; they are derived from classical tables.

References:
- Astrodienst Egyptian terms (gch_terms) — half-open segments at listed division degrees
- Chaldean decans (gch_decans)

Term (حد) lookup follows the Astrodienst / Ptolemy Egyptian table: a planet at an
exact division degree belongs to the next bound (e.g. 25.00° Aquarius = Saturn).
For night charts, Mercury and Saturn are exchanged (per Astrodienst note).
"""

from typing import Dict, List, Tuple

# Dorothean triplicity by element (day / night / participating)
TRIPLICITY_BY_ELEMENT = {
    'fire': {'day': 'Sun', 'night': 'Jupiter', 'participating': 'Saturn'},
    'earth': {'day': 'Venus', 'night': 'Moon', 'participating': 'Mars'},
    'air': {'day': 'Saturn', 'night': 'Mercury', 'participating': 'Jupiter'},
    'water': {'day': 'Venus', 'night': 'Mars', 'participating': 'Moon'},
}

SIGN_ELEMENTS = [
    'fire', 'earth', 'air', 'water',
    'fire', 'earth', 'air', 'water',
    'fire', 'earth', 'air', 'water',
]

# Egyptian terms: division degrees within sign + rulers for each segment (Astrodienst).
EGYPTIAN_TERM_TABLE: List[Tuple[List[float], List[str]]] = [
    ([0, 6, 12, 20, 25], ['Jupiter', 'Venus', 'Mercury', 'Mars', 'Saturn']),
    ([0, 8, 14, 22, 27], ['Venus', 'Mercury', 'Jupiter', 'Saturn', 'Mars']),
    ([0, 6, 12, 17, 24], ['Mercury', 'Jupiter', 'Venus', 'Mars', 'Saturn']),
    ([0, 7, 13, 19, 26], ['Mars', 'Venus', 'Mercury', 'Jupiter', 'Saturn']),
    ([0, 6, 11, 18, 24], ['Jupiter', 'Venus', 'Saturn', 'Mercury', 'Mars']),
    ([0, 7, 17, 21, 28], ['Mercury', 'Venus', 'Jupiter', 'Mars', 'Saturn']),
    ([0, 6, 14, 21, 28], ['Saturn', 'Mercury', 'Jupiter', 'Venus', 'Mars']),
    ([0, 7, 11, 19, 24], ['Mars', 'Venus', 'Mercury', 'Jupiter', 'Saturn']),
    ([0, 12, 17, 21, 26], ['Jupiter', 'Venus', 'Mercury', 'Saturn', 'Mars']),
    ([0, 7, 14, 22, 26], ['Mercury', 'Jupiter', 'Venus', 'Saturn', 'Mars']),
    ([0, 7, 13, 20, 25], ['Mercury', 'Venus', 'Jupiter', 'Mars', 'Saturn']),
    ([0, 12, 16, 19, 28], ['Venus', 'Jupiter', 'Mercury', 'Mars', 'Saturn']),
]

# Chaldean decan (face) rulers from 0° Aries, repeating every 7 decans of 10°
CHALDEAN_DECAN_RULERS = ['Mars', 'Sun', 'Venus', 'Mercury', 'Moon', 'Saturn', 'Jupiter']


def chart_is_diurnal(sun_house: int) -> bool:
    """Day chart when the Sun is above the horizon (houses 7-12)."""
    return sun_house in (7, 8, 9, 10, 11, 12)


def get_triplicity_rulers(sign_index: int, is_diurnal: bool) -> Dict[str, str]:
    """Dorothean triplicity: primary (sect), secondary (other sect), participating (شریک)."""
    element = SIGN_ELEMENTS[sign_index]
    rulers = TRIPLICITY_BY_ELEMENT[element]
    if is_diurnal:
        primary, secondary = rulers['day'], rulers['night']
    else:
        primary, secondary = rulers['night'], rulers['day']
    return {
        'triplicity': primary,
        'triplicity_2': secondary,
        'participating': rulers['participating'],
    }


def get_triplicity_ruler(sign_index: int, is_diurnal: bool) -> str:
    return get_triplicity_rulers(sign_index, is_diurnal)['triplicity']


def _normalize_degree_in_sign(degree_in_sign: float) -> float:
    degree = degree_in_sign % 30
    if degree < 0:
        degree += 30
    if degree >= 30:
        degree = 0.0
    return degree


def get_term_ruler(sign_index: int, degree_in_sign: float, is_diurnal: bool = True) -> str:
    """
    Egyptian term ruler using Astrodienst half-open bounds.

    At exact division degrees the next bound applies (e.g. 21° Libra = Venus).
    Night charts exchange Mercury and Saturn (Astrodienst Egyptian terms note).
    """
    degree = _normalize_degree_in_sign(degree_in_sign)
    boundaries, planets = EGYPTIAN_TERM_TABLE[sign_index]

    ruler = planets[-1]
    for idx, boundary in enumerate(boundaries):
        if degree >= boundary:
            ruler = planets[idx]

    if not is_diurnal:
        if ruler == 'Mercury':
            return 'Saturn'
        if ruler == 'Saturn':
            return 'Mercury'
    return ruler


def get_face_ruler(sign_index: int, degree_in_sign: float) -> str:
    """
    Face (وجه) / decan ruler via the Chaldean sequence from 0° Aries.
    Each sign has three 10-degree faces: 0-9, 10-19, 20-29.
    """
    degree = _normalize_degree_in_sign(degree_in_sign)
    decan_in_sign = min(int(degree // 10), 2)
    global_decan_index = sign_index * 3 + decan_in_sign
    return CHALDEAN_DECAN_RULERS[global_decan_index % len(CHALDEAN_DECAN_RULERS)]


def get_minor_dignity_rulers(sign_index: int, degree_in_sign: float, is_diurnal: bool) -> Dict[str, str]:
    triplicity = get_triplicity_rulers(sign_index, is_diurnal)
    return {
        **triplicity,
        'term': get_term_ruler(sign_index, degree_in_sign, is_diurnal),
        'face': get_face_ruler(sign_index, degree_in_sign),
    }


# Major essential dignities: rulership/detriment by whole sign; exaltation/fall by exact degree.
# Exaltation degrees follow the classical (Ptolemaic) table; fall is the opposite degree in the opposite sign.
EXALTATION_FALL_ORB = 1.0  # degrees from exact exaltation / fall degree

MAJOR_ESSENTIAL_DIGNITIES: Dict[str, Dict] = {
    'Sun': {
        'rulership': [4],
        'detriment': [10],
        'exaltation': (0, 19),
        'fall': (6, 19),
    },
    'Moon': {
        'rulership': [3],
        'detriment': [9],
        'exaltation': (1, 3),
        'fall': (7, 3),
    },
    'Mercury': {
        'rulership': [2, 5],
        'detriment': [8, 11],
        'exaltation': (5, 15),
        'fall': (11, 15),
    },
    'Venus': {
        'rulership': [1, 6],
        'detriment': [0, 7],
        'exaltation': (11, 27),
        'fall': (5, 27),
    },
    'Mars': {
        'rulership': [0, 7],
        'detriment': [1, 6],
        'exaltation': (9, 28),
        'fall': (3, 28),
    },
    'Jupiter': {
        'rulership': [8, 11],
        'detriment': [2, 5],
        'exaltation': (3, 15),
        'fall': (9, 15),
    },
    'Saturn': {
        'rulership': [9, 10],
        'detriment': [3, 4],
        'exaltation': (6, 21),
        'fall': (0, 21),
    },
    # Outer planets: no classical degree table (Lehman, Wikipedia). Signs follow common
    # modern proposals; degree set to 15° as neutral peak within the sign.
    # Uranus — exalt Scorpio / fall Taurus (Gur, Tarot.com, Wikipedia)
    'Uranus': {
        'rulership': [10],
        'detriment': [4],
        'exaltation': (7, 15),
        'fall': (1, 15),
    },
    # Neptune — exalt Aquarius / fall Leo (Dima Gur; fall opposite exaltation)
    'Neptune': {
        'rulership': [11],
        'detriment': [5],
        'exaltation': (10, 15),
        'fall': (4, 15),
    },
    # Pluto — exalt Leo / fall Aquarius (Gur, Wikipedia modern practice)
    'Pluto': {
        'rulership': [7],
        'detriment': [1],
        'exaltation': (4, 15),
        'fall': (10, 15),
    },
    # Lunar nodes — Al-Biruni / Al-Qabisi / Wikipedia: Caput 3° Gemini, Cauda 3° Sagittarius
    'NorthNode': {
        'rulership': [],
        'detriment': [],
        'exaltation': (2, 3),
        'fall': (8, 3),
    },
    'SouthNode': {
        'rulership': [],
        'detriment': [],
        'exaltation': (8, 3),
        'fall': (2, 3),
    },
}


DIGNITY_FA = {
    'fall_degree': 'درجه هبوط',
    'detriment': 'وبال',
    'fall_sign': 'برج هبوط',
    'exaltation_sign': 'برج شرف',
    'rulership': 'سروری',
    'exaltation_degree': 'درجه شرف',
}

# Weakest (1) → strongest (6); background / text for table cells and legend.
DIGNITY_SPECTRUM = {
    'fall_degree': ('#4a0e0e', '#ffffff'),
    'detriment': ('#a93226', '#ffffff'),
    'fall_sign': ('#f0b4b4', '#5c2020'),
    'exaltation_sign': ('#b8e6b8', '#1a4d1a'),
    'rulership': ('#27ae60', '#ffffff'),
    'exaltation_degree': ('#0b5345', '#ffffff'),
}


def get_major_essential_dignity(
    planet_name: str,
    sign_index: int,
    degree_in_sign: float,
    orb: float = EXALTATION_FALL_ORB,
) -> str | None:
    """
    Return the dominant major essential dignity (strongest match wins).

    Six levels (weak → strong): fall_degree, detriment, fall_sign, exaltation_sign,
    rulership, exaltation_degree.
    """
    data = MAJOR_ESSENTIAL_DIGNITIES.get(planet_name)
    if not data:
        return None

    ex_sign, ex_deg = data['exaltation']
    fall_sign, fall_deg = data['fall']
    at_exalt_degree = sign_index == ex_sign and abs(degree_in_sign - ex_deg) <= orb
    at_fall_degree = sign_index == fall_sign and abs(degree_in_sign - fall_deg) <= orb

    if at_exalt_degree:
        return 'exaltation_degree'
    if sign_index in data['rulership']:
        return 'rulership'
    if sign_index == ex_sign:
        return 'exaltation_sign'
    if at_fall_degree:
        return 'fall_degree'
    if sign_index in data['detriment']:
        return 'detriment'
    if sign_index == fall_sign:
        return 'fall_sign'

    return None


def get_dignity_fa(dignity: str | None) -> str:
    if not dignity:
        return ''
    return DIGNITY_FA.get(dignity, '')


def format_dignity_cell_html(dignity: str | None, dignity_fa: str = '') -> str:
    """Essential-dignity table cell with spectrum coloring."""
    if not dignity:
        return '<td class="dignity-cell">-</td>'
    label = dignity_fa or get_dignity_fa(dignity)
    colors = DIGNITY_SPECTRUM.get(dignity)
    if not colors:
        return f'<td class="dignity-cell">{label}</td>'
    bg, fg = colors
    return (
        f'<td class="dignity-cell dignity--{dignity}" '
        f'style="background:{bg} !important;color:{fg};font-weight:700;">{label}</td>'
    )
