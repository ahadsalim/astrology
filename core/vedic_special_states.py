# -*- coding: utf-8 -*-
"""
Vedic special degree states (sidereal / Lahiri), for display in the planets table.

- Pushkara Navamsa (پوشکار ناوامشا): navamsa sign is Taurus, Cancer, Virgo, Libra, Sag, or Pisces
- Vargottama (وارگوتاما)
- Ashtamamsa (آشتامشا): Navamsa sign is the 8th from Rashi sign
- Gandanta (گاندانتا): last 3°20' of water signs or first 3°20' of fire signs (strict arc)
"""

from typing import List, Tuple

NAVAMSA_ARC = 30 / 9  # 3°20'

CHARA_SIGNS = {0, 3, 6, 9}
STHIRA_SIGNS = {1, 4, 7, 10}
DVISVA_SIGNS = {2, 5, 8, 11}

WATER_SIGNS = {3, 7, 11}
FIRE_SIGNS = {0, 4, 8}

GANDANTA_ARC = 10 / 3  # 3°20'

# Navamsa signs ruled by benefics (Pushkara Navamsa)
PUSHKARA_NAVAMSA_SIGNS = {1, 3, 5, 6, 8, 11}  # Taurus, Cancer, Virgo, Libra, Sag, Pisces

STATE_LABELS = {
    'pushkara_navamsa': 'پوشکار ناوامشا',
    'vargottama': 'وارگوتاما',
    'ashtamamsa': 'آشتامشا',
    'gandanta': 'گاندانتا',
}


def sidereal_sign_and_degree(sidereal_longitude: float) -> Tuple[int, float]:
    lon = sidereal_longitude % 360
    sign = int(lon // 30) % 12
    return sign, lon % 30


def navamsa_sign_index(sidereal_longitude: float) -> int:
    """Parashari Navamsa (D9) sign from sidereal longitude."""
    sign, degree = sidereal_sign_and_degree(sidereal_longitude)
    pada = int(degree / NAVAMSA_ARC)

    if sign in CHARA_SIGNS:
        start = sign
    elif sign in STHIRA_SIGNS:
        start = (sign + 8) % 12
    else:
        start = (sign + 4) % 12

    return (start + pada) % 12


def is_pushkara_navamsa(sidereal_longitude: float) -> bool:
    """Pushkara when the planet's navamsa (D9) sign is a benefic navamsa sign."""
    return navamsa_sign_index(sidereal_longitude) in PUSHKARA_NAVAMSA_SIGNS


def is_vargottama(rashi_sign: int, navamsa_sign: int) -> bool:
    return rashi_sign == navamsa_sign


def is_ashtamamsa(rashi_sign: int, navamsa_sign: int) -> bool:
    """Navamsa sign falls in the 8th house/sign from Rashi."""
    return (navamsa_sign - rashi_sign) % 12 == 7


def is_gandanta(sign: int, degree_in_sign: float) -> bool:
    """
    Gandanta zones: last 3°20' of water signs (inclusive) or first 3°20' of fire signs (exclusive end).

    A planet a few arcseconds past 3°20'00" in a fire sign is outside Gandanta.
    """
    degree = degree_in_sign % 30
    if sign in WATER_SIGNS and degree >= (30 - GANDANTA_ARC):
        return True
    if sign in FIRE_SIGNS and degree < GANDANTA_ARC:
        return True
    return False


def get_vedic_special_states(sidereal_longitude: float) -> List[str]:
    """
    Return Persian labels for active Vedic states at this sidereal position.
    """
    rashi_sign, degree = sidereal_sign_and_degree(sidereal_longitude)
    navamsa_sign = navamsa_sign_index(sidereal_longitude)

    states = []
    if is_pushkara_navamsa(sidereal_longitude):
        states.append(STATE_LABELS['pushkara_navamsa'])
    if is_vargottama(rashi_sign, navamsa_sign):
        states.append(STATE_LABELS['vargottama'])
    if is_ashtamamsa(rashi_sign, navamsa_sign):
        states.append(STATE_LABELS['ashtamamsa'])
    if is_gandanta(rashi_sign, degree):
        states.append(STATE_LABELS['gandanta'])

    return states


def format_vedic_special_states(sidereal_longitude: float) -> str:
    states = get_vedic_special_states(sidereal_longitude)
    return ' / '.join(states) if states else '—'


STATE_STYLE_KEYS = {
    STATE_LABELS['pushkara_navamsa']: 'pushkara',
    STATE_LABELS['vargottama']: 'vargottama',
    STATE_LABELS['ashtamamsa']: 'ashtamamsa',
    STATE_LABELS['gandanta']: 'gandanta',
}


def vedic_states_td_class(states: List[str]) -> str:
    """CSS class for the Vedic states table cell."""
    if not states:
        return 'vedic-td vedic-td--empty'
    if len(states) == 1:
        key = STATE_STYLE_KEYS[states[0]]
        return f'vedic-td vedic-td--{key}'
    return 'vedic-td vedic-td--multi'


def format_vedic_states_cell_html(states: List[str]) -> str:
    """
    HTML for the Vedic states cell.
    One state: plain text (background on <td>).
    Two or more: white cell, each label with its own font color.
    """
    if not states:
        return '—'
    if len(states) == 1:
        return states[0]
    parts = []
    for label in states:
        key = STATE_STYLE_KEYS[label]
        parts.append(f'<span class="vedic-label vedic-label--{key}">{label}</span>')
    return ' <span class="vedic-sep">/</span> '.join(parts)
