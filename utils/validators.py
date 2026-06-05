import re
from datetime import datetime
import jdatetime
from data import get_city_info

class ValidationError(Exception):
    """Custom validation error"""
    pass

class InputValidator:
    """Validates user inputs"""
    
    @staticmethod
    def validate_name(name):
        """Validate name input"""
        if not name or len(name.strip()) == 0:
            raise ValidationError("نام نمی‌تواند خالی باشد")
        if len(name) > 100:
            raise ValidationError("نام نمی‌تواند بیشتر از 100 کاراکتر باشد")
        return name.strip()
    
    @staticmethod
    def validate_persian_date(date_str):
        """Validate Persian date format (YYYY-MM-DD or DD-MM-YYYY)"""
        if not date_str:
            raise ValidationError("تاریخ نمی‌تواند خالی باشد")
        
        # Try different formats
        formats = [
            r'^\d{4}-\d{1,2}-\d{1,2}$',  # 1400-05-12
            r'^\d{1,2}-\d{1,2}-\d{4}$',  # 12-05-1400
        ]
        
        if not any(re.match(fmt, date_str) for fmt in formats):
            raise ValidationError("فرمت تاریخ نامعتبر است. مثال: 1400-05-12 یا 12-05-1400")
        
        # Parse and validate
        try:
            parts = date_str.split('-')
            if len(parts[0]) == 4:  # YYYY-MM-DD
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            else:  # DD-MM-YYYY
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            
            # Validate ranges
            if year < 1300 or year > 1450:
                raise ValidationError("سال باید بین 1300 تا 1450 باشد")
            if month < 1 or month > 12:
                raise ValidationError("ماه باید بین 1 تا 12 باشد")
            if day < 1 or day > 31:
                raise ValidationError("روز باید بین 1 تا 31 باشد")
            
            # Try to create jdatetime object
            jdatetime.date(year, month, day)
            
            # Return normalized format (YYYY-MM-DD)
            return f"{year}-{month:02d}-{day:02d}"
            
        except (ValueError, jdatetime.GregorianToJalali.InvalidJalaliDate) as e:
            raise ValidationError(f"تاریخ نامعتبر است: {str(e)}")
    
    @staticmethod
    def validate_time(time_str):
        """Validate time format (HH:MM)"""
        if not time_str:
            raise ValidationError("ساعت نمی‌تواند خالی باشد")
        
        if not re.match(r'^\d{1,2}:\d{2}$', time_str):
            raise ValidationError("فرمت ساعت نامعتبر است. مثال: 14:30")
        
        try:
            hour, minute = map(int, time_str.split(':'))
            if hour < 0 or hour > 23:
                raise ValidationError("ساعت باید بین 0 تا 23 باشد")
            if minute < 0 or minute > 59:
                raise ValidationError("دقیقه باید بین 0 تا 59 باشد")
            
            return f"{hour:02d}:{minute:02d}"
        except ValueError:
            raise ValidationError("فرمت ساعت نامعتبر است")
    
    @staticmethod
    def validate_place(place):
        """Validate place input (must be a city from database)"""
        if not place or len(place.strip()) == 0:
            raise ValidationError("محل تولد نمی‌تواند خالی باشد")
        
        place = place.strip()
        
        # Check if city exists in database
        city_info = get_city_info(place)
        if not city_info:
            raise ValidationError(f"شهر '{place}' در دیتابیس یافت نشد. لطفاً از لیست شهرها انتخاب کنید.")
        
        return place
    
    @staticmethod
    def validate_vision(vision):
        """Validate vision input (optional)"""
        if not vision:
            return ""
        if len(vision) > 500:
            raise ValidationError("دغدغه اصلی نمی‌تواند بیشتر از 500 کاراکتر باشد")
        return vision.strip()
    
    @staticmethod
    def validate_all(name, date, time, place, vision=""):
        """Validate all inputs at once"""
        return {
            'name': InputValidator.validate_name(name),
            'date': InputValidator.validate_persian_date(date),
            'time': InputValidator.validate_time(time),
            'place': InputValidator.validate_place(place),
            'vision': InputValidator.validate_vision(vision)
        }
