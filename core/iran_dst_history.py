# -*- coding: utf-8 -*-
"""
Iran Daylight Saving Time (DST) History Database
Based on official records and Wikipedia documentation
"""

# DST History in Iran:
# - Started: 1977 (1356 شمسی)
# - Abolished: 2006-2008 (1385-1387 شمسی)
# - Restored: March 21, 2008 (1 فروردین 1387)
# - Permanently Abolished: September 21, 2022 (30 شهریور 1401)
# - Partially Restored in Tehran: May 2025 (but not nationwide)

# For astrological calculations, we use the official nationwide DST rules

IRAN_DST_RULES = {
    # DST was NOT observed in these periods:
    'no_dst_periods': [
        # Before DST started
        (None, 1977),
        # Abolished period under Ahmadinejad
        (2006, 2008),
        # Permanently abolished (from Sept 21, 2022 onwards)
        (2022, None)  # From Sept 21, 2022 onwards, no DST
    ],
    
    # DST was observed in these periods:
    'dst_periods': [
        # First period: 1977-2005
        (1977, 2005),
        # Second period: 2008-2022 (until Sept 21)
        (2008, 2022)
    ],
    
    # DST transition dates (when DST was active):
    # Start: 1 Farvardin (March 20/21) at midnight -> clocks forward 1 hour
    # End: 30 Shahrivar (September 20/21) at midnight -> clocks backward 1 hour
    'transition_rules': {
        'start_month': 3,      # March
        'start_day_range': (20, 21),  # Depends on equinox
        'end_month': 9,        # September
        'end_day_range': (20, 21)
    }
}


def is_dst_active_in_year(year):
    """
    Check if DST was active in a given year in Iran
    
    Args:
        year: Gregorian year
        
    Returns:
        bool: True if DST was observed that year, False otherwise
    """
    # Check no_dst_periods
    for start, end in IRAN_DST_RULES['no_dst_periods']:
        if start is None and year < end:
            return False
        if end is None and year >= start:
            return False
        if start is not None and end is not None:
            if start <= year < end:
                return False
    
    # Check dst_periods
    for start, end in IRAN_DST_RULES['dst_periods']:
        if start <= year <= end:
            return True
    
    return False


def should_apply_dst(year, month, day):
    """
    Determine if DST should be applied for a specific date
    
    Args:
        year: Gregorian year
        month: Month (1-12)
        day: Day of month
        
    Returns:
        bool: True if DST should be applied, False otherwise
        
    Note:
        For 2022, DST was abolished on September 21, so dates after that don't use DST
    """
    # First check if DST was active in this year
    if not is_dst_active_in_year(year):
        return False
    
    # Special case for 2022: DST ended on September 21
    if year == 2022:
        if month > 9:  # October onwards
            return False
        if month == 9 and day >= 21:  # Sept 21 onwards
            return False
    
    # For years with DST, check if date is in DST period
    # DST runs from March 20/21 to September 20/21
    
    # Before March: no DST
    if month < 3:
        return False
    
    # After September: no DST
    if month > 9:
        return False
    
    # March: DST starts around 20-21
    if month == 3:
        return day >= 20  # Conservative: assume DST starts on 20th
    
    # September: DST ends around 20-21
    if month == 9:
        return day < 21  # Conservative: assume DST ends on 21st
    
    # April to August: always DST
    return True


def get_dst_info(year):
    """
    Get DST information for a specific year
    
    Args:
        year: Gregorian year
        
    Returns:
        dict: Information about DST for that year
    """
    active = is_dst_active_in_year(year)
    
    info = {
        'year': year,
        'dst_active': active,
        'reason': ''
    }
    
    if year < 1977:
        info['reason'] = 'DST not yet introduced'
    elif 2006 <= year < 2008:
        info['reason'] = 'DST abolished by President Ahmadinejad (2006-2008)'
    elif year >= 2022:
        if year == 2022:
            info['reason'] = 'DST permanently abolished on September 21, 2022'
        else:
            info['reason'] = 'DST permanently abolished (since 2022)'
    elif active:
        info['reason'] = 'DST active (March 20/21 to September 20/21)'
    
    return info


# Historical DST dates for reference
HISTORICAL_DST_DATES = """
Iran DST History:

1977-2005: DST observed
  - Start: 1 Farvardin (March 20/21) 00:00 -> 01:00
  - End: 30 Shahrivar (September 20/21) 00:00 -> 23:00 (previous day)

2006-2007: DST abolished by President Mahmoud Ahmadinejad

2008-2022 (until Sept 21): DST restored
  - Start: 1 Farvardin (March 20/21) 00:00 -> 01:00
  - End: 30 Shahrivar (September 20/21) 00:00 -> 23:00 (previous day)

September 21, 2022: DST permanently abolished
  - Iran now observes UTC+3:30 year-round

2025: Partial restoration in Tehran only (not nationwide, not used in calculations)

For astrological calculations:
- Use UTC+3:30 as base timezone
- Apply DST (+1 hour) only for dates when DST was officially active nationwide
- Do NOT apply DST for dates after September 21, 2022
"""
