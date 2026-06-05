# -*- coding: utf-8 -*-
"""Format geographic latitude/longitude as degrees, minutes, and seconds."""


def decimal_to_dms(value: float) -> tuple:
    """
    Convert decimal degrees to (degrees, minutes, seconds).

    Returns absolute DMS components; sign is handled separately by callers.
    """
    value = abs(float(value))
    degrees = int(value)
    minutes_float = (value - degrees) * 60
    minutes = int(minutes_float)
    seconds = round((minutes_float - minutes) * 60)

    if seconds >= 60:
        seconds = 0
        minutes += 1
    if minutes >= 60:
        minutes = 0
        degrees += 1

    return degrees, minutes, seconds


def format_latitude(latitude: float) -> str:
    """Format latitude as DMS with Persian direction (شمالی/جنوبی)."""
    direction = 'شمالی' if latitude >= 0 else 'جنوبی'
    d, m, s = decimal_to_dms(latitude)
    return f"{d}° {m:02d}′ {s:02d}″ {direction}"


def format_longitude(longitude: float) -> str:
    """Format longitude as DMS with Persian direction (شرقی/غربی)."""
    direction = 'شرقی' if longitude >= 0 else 'غربی'
    d, m, s = decimal_to_dms(longitude)
    return f"{d}° {m:02d}′ {s:02d}″ {direction}"


def format_coordinates(latitude: float, longitude: float, separator: str = ' — ') -> str:
    """Format lat/lon pair for display."""
    return f"عرض: {format_latitude(latitude)}{separator}طول: {format_longitude(longitude)}"


def format_arc_dms(arc_degrees: float) -> str:
    """Format an ecliptic arc (longitude, degree-in-sign, aspect, orb) as D° MM′ SS″."""
    d, m, s = decimal_to_dms(arc_degrees)
    return f"{d}° {m:02d}′ {s:02d}″"


def format_arc_dms_html(arc_degrees: float) -> str:
    """Format arc degrees as DMS wrapped for HTML tables (LTR isolation)."""
    return f'<span class="arc-dms">{format_arc_dms(arc_degrees)}</span>'
