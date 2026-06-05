# -*- coding: utf-8 -*-
"""
Date and Time Utilities for Astrology Calculations
Handles Jalali to Gregorian conversion and timezone management
"""

import jdatetime
from datetime import datetime, timedelta
import pytz
import logging
from .iran_dst_history import should_apply_dst, get_dst_info

logger = logging.getLogger(__name__)

# Iran timezone (base UTC+3:30)
IRAN_TZ = pytz.timezone('Asia/Tehran')

# Iran Standard Time offset (without DST)
IRAN_STD_OFFSET = timedelta(hours=3, minutes=30)

# Iran Daylight Time offset (with DST)
IRAN_DST_OFFSET = timedelta(hours=4, minutes=30)


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
        Convert local time to UTC considering timezone and DST
        Uses accurate Iran DST history (1977-2005, 2008-2022 Sept 21)
        
        Args:
            gregorian_date: datetime.date object
            local_time_str: String in format "HH:MM"
            timezone: pytz timezone object (default: Asia/Tehran)
            
        Returns:
            dict with UTC datetime components and Julian Day
        """
        try:
            # Parse time
            hour, minute = map(int, local_time_str.split(':'))
            
            # Create naive datetime
            naive_dt = datetime(
                gregorian_date.year,
                gregorian_date.month,
                gregorian_date.day,
                hour,
                minute,
                0
            )
            
            # Check if DST should be applied based on Iran's official history
            use_dst = should_apply_dst(
                gregorian_date.year,
                gregorian_date.month,
                gregorian_date.day
            )
            
            # Get DST info for logging
            dst_info = get_dst_info(gregorian_date.year)
            
            if use_dst:
                # Apply DST: UTC+4:30
                offset = IRAN_DST_OFFSET
                logger.info(f"Applying DST for {gregorian_date}: {dst_info['reason']}")
            else:
                # Standard time: UTC+3:30
                offset = IRAN_STD_OFFSET
                logger.info(f"No DST for {gregorian_date}: {dst_info['reason']}")
            
            # Create timezone-aware datetime with correct offset
            # We manually apply offset instead of using pytz localize
            # to avoid issues with Iran's complex DST history
            utc_dt = naive_dt - offset
            
            # Calculate decimal hour for Julian Day
            utc_hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
            
            # Format offset string
            offset_hours = int(offset.total_seconds() // 3600)
            offset_minutes = int((offset.total_seconds() % 3600) // 60)
            offset_str = f"+{offset_hours:02d}:{offset_minutes:02d}"
            
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
                'utc_offset': offset_str,
                'dst_applied': use_dst,
                'dst_info': dst_info['reason']
            }
            
            logger.info(f"Converted local {naive_dt} to UTC {utc_dt} (DST: {use_dst})")
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
