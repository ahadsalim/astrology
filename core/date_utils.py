# -*- coding: utf-8 -*-
"""
Date and Time Utilities for Astrology Calculations
Handles Jalali to Gregorian conversion and timezone management
"""

import jdatetime
from datetime import datetime
import pytz
import logging
from .iran_dst_history import iran_offset_for_jalali

logger = logging.getLogger(__name__)

# Kept so existing callers can still pass the Tehran zone object.
# The offset itself is NOT taken from this zone. IANA Asia/Tehran disagrees
# with the Solar Hijri rules required for Iranian birth charts; the offset
# comes only from iran_offset_for_jalali.
IRAN_TZ = pytz.timezone('Asia/Tehran')


class DateTimeConverter:
    """Handles date and time conversions for astrological calculations"""
    
    @staticmethod
    def jalali_to_gregorian(jalali_date_str):
        """
        Convert Jalali (Persian) date to Gregorian
        
        Args:
            jalali_date_str: String in format "YYYY-MM-DD" or "DD-MM-YYYY"
            
        Returns:
            datetime.date object in Gregorian calendar
            
        Raises:
            ValueError: If date format is invalid
        """
        try:
            # Try YYYY-MM-DD format first
            if '-' in jalali_date_str:
                parts = jalali_date_str.split('-')
                if len(parts) == 3:
                    # Detect format based on first number
                    if int(parts[0]) > 1300:  # YYYY-MM-DD
                        year, month, day = map(int, parts)
                    else:  # DD-MM-YYYY
                        day, month, year = map(int, parts)
                    
                    # Create Jalali date and convert
                    j_date = jdatetime.date(year, month, day)
                    g_date = j_date.togregorian()
                    
                    logger.info(f"Converted Jalali {jalali_date_str} to Gregorian {g_date}")
                    return g_date
            
            raise ValueError(f"Invalid date format: {jalali_date_str}")
            
        except Exception as e:
            logger.error(f"Error converting Jalali date: {e}")
            raise ValueError(f"تاریخ نامعتبر است: {jalali_date_str}")
    
    @staticmethod
    def local_to_utc(gregorian_date, local_time_str, timezone=IRAN_TZ):
        """
        Convert an Iranian local civil time to UTC.

        The Gregorian date is turned back into the Solar Hijri date with the
        same ``jdatetime`` conversion the rest of the app uses, then the
        offset is taken from ``iran_offset_for_jalali``. ``timezone`` is
        accepted for compatibility and is not consulted: every seeded city
        is Asia/Tehran, and that IANA zone is not the chart rule.

        Args:
            gregorian_date: datetime.date (or datetime) object
            local_time_str: String in format "HH:MM"
            timezone: ignored; retained so existing callers keep working

        Returns:
            dict with UTC datetime components and the offset that was applied
        """
        del timezone  # chart offsets do not follow IANA; see iran_dst_history
        try:
            if isinstance(gregorian_date, datetime):
                gregorian_date = gregorian_date.date()

            hour, minute = map(int, local_time_str.split(':'))

            naive_dt = datetime(
                gregorian_date.year,
                gregorian_date.month,
                gregorian_date.day,
                hour,
                minute,
                0
            )

            jalali = jdatetime.date.fromgregorian(date=gregorian_date)
            offset_info = iran_offset_for_jalali(
                jalali.year, jalali.month, jalali.day, hour, minute
            )
            offset = offset_info['offset']
            utc_dt = naive_dt - offset

            utc_hour_decimal = (
                utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
            )

            result = {
                'year': utc_dt.year,
                'month': utc_dt.month,
                'day': utc_dt.day,
                'hour': utc_dt.hour,
                'minute': utc_dt.minute,
                'second': utc_dt.second,
                'hour_decimal': utc_hour_decimal,
                'utc_datetime': utc_dt,
                'local_datetime': naive_dt,
                'timezone_name': 'Asia/Tehran',
                'utc_offset': offset_info['offset_str'],
                'dst_applied': offset_info['dst_applied'],
                'dst_info': offset_info['rule'],
                'local_time_status': offset_info['local_time_status'],
                'transition_resolution': offset_info['resolution'],
                'jalali_year': jalali.year,
                'jalali_month': jalali.month,
                'jalali_day': jalali.day,
            }

            logger.info(
                "Converted local %s to UTC %s (offset %s, %s, %s)",
                naive_dt,
                utc_dt,
                offset_info['offset_str'],
                offset_info['local_time_status'],
                offset_info['rule'],
            )
            return result

        except Exception as e:
            logger.error(f"Error converting time: {e}")
            raise ValueError(f"خطا در تبدیل زمان: {str(e)}")
    
    @staticmethod
    def calculate_julian_day(utc_year, utc_month, utc_day, utc_hour_decimal):
        """
        Calculate Julian Day Number
        
        Args:
            utc_year: Year in UTC
            utc_month: Month in UTC
            utc_day: Day in UTC
            utc_hour_decimal: Hour in decimal format (e.g., 14.5 for 14:30)
            
        Returns:
            float: Julian Day Number
        """
        import swisseph as swe
        
        jd = swe.julday(utc_year, utc_month, utc_day, utc_hour_decimal)
        logger.info(f"Julian Day: {jd}")
        return jd
    
    @staticmethod
    def parse_and_convert(jalali_date_str, local_time_str, timezone=IRAN_TZ):
        """
        Complete conversion from Jalali date and local time to Julian Day
        
        Args:
            jalali_date_str: Jalali date string
            local_time_str: Local time string
            timezone: Timezone object
            
        Returns:
            dict with all conversion data including Julian Day
        """
        # Convert Jalali to Gregorian
        gregorian_date = DateTimeConverter.jalali_to_gregorian(jalali_date_str)
        
        # Convert local time to UTC
        utc_data = DateTimeConverter.local_to_utc(gregorian_date, local_time_str, timezone)
        
        # Calculate Julian Day
        jd = DateTimeConverter.calculate_julian_day(
            utc_data['year'],
            utc_data['month'],
            utc_data['day'],
            utc_data['hour_decimal']
        )
        
        # Combine all data
        result = {
            'jalali_date': jalali_date_str,
            'gregorian_date': gregorian_date,
            'gregorian_str': gregorian_date.strftime('%Y-%m-%d'),
            'local_time': local_time_str,
            'utc_time': f"{utc_data['hour']:02d}:{utc_data['minute']:02d}",
            'julian_day': jd,
            'timezone': utc_data['timezone_name'],
            'utc_offset': utc_data['utc_offset'],
            'dst_applied': utc_data['dst_applied'],
            'dst_info': utc_data['dst_info'],
            'local_time_status': utc_data['local_time_status'],
            'transition_resolution': utc_data['transition_resolution'],
            'utc_datetime': utc_data['utc_datetime'],
            'local_datetime': utc_data['local_datetime']
        }
        
        return result


def validate_jalali_date(date_str):
    """Validate Jalali date format and range"""
    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            return False
        
        if int(parts[0]) > 1300:  # YYYY-MM-DD
            year, month, day = map(int, parts)
        else:  # DD-MM-YYYY
            day, month, year = map(int, parts)
        
        # Validate ranges
        if not (1300 <= year <= 1500):
            return False
        if not (1 <= month <= 12):
            return False
        if not (1 <= day <= 31):
            return False
        
        # Try to create the date
        jdatetime.date(year, month, day)
        return True
        
    except:
        return False


def validate_time(time_str):
    """Validate time format HH:MM"""
    try:
        parts = time_str.split(':')
        if len(parts) != 2:
            return False
        
        hour, minute = map(int, parts)
        return 0 <= hour <= 23 and 0 <= minute <= 59
        
    except:
        return False
