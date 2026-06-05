# -*- coding: utf-8 -*-
"""
Iranian Cities Database with Geographic Coordinates
All coordinates are in decimal degrees format
Timezone: Asia/Tehran (UTC+3:30, DST: UTC+4:30)
"""

IRANIAN_CITIES = {
    "تهران": {
        "name_en": "Tehran",
        "lat": 35.6892,
        "lon": 51.3890,
        "timezone": "Asia/Tehran"
    },
    "مشهد": {
        "name_en": "Mashhad",
        "lat": 36.2974,
        "lon": 59.6067,
        "timezone": "Asia/Tehran"
    },
    "اصفهان": {
        "name_en": "Isfahan",
        "lat": 32.6546,
        "lon": 51.6680,
        "timezone": "Asia/Tehran"
    },
    "شیراز": {
        "name_en": "Shiraz",
        "lat": 29.5918,
        "lon": 52.5836,
        "timezone": "Asia/Tehran"
    },
    "تبریز": {
        "name_en": "Tabriz",
        "lat": 38.0800,
        "lon": 46.2919,
        "timezone": "Asia/Tehran"
    },
    "کرج": {
        "name_en": "Karaj",
        "lat": 35.8327,
        "lon": 50.9916,
        "timezone": "Asia/Tehran"
    },
    "اهواز": {
        "name_en": "Ahvaz",
        "lat": 31.3183,
        "lon": 48.6706,
        "timezone": "Asia/Tehran"
    },
    "قم": {
        "name_en": "Qom",
        "lat": 34.6416,
        "lon": 50.8746,
        "timezone": "Asia/Tehran"
    },
    "کرمانشاه": {
        "name_en": "Kermanshah",
        "lat": 34.3142,
        "lon": 47.0650,
        "timezone": "Asia/Tehran"
    },
    "ارومیه": {
        "name_en": "Urmia",
        "lat": 37.5527,
        "lon": 45.0761,
        "timezone": "Asia/Tehran"
    },
    "رشت": {
        "name_en": "Rasht",
        "lat": 37.2808,
        "lon": 49.5832,
        "timezone": "Asia/Tehran"
    },
    "زاهدان": {
        "name_en": "Zahedan",
        "lat": 29.4963,
        "lon": 60.8629,
        "timezone": "Asia/Tehran"
    },
    "کرمان": {
        "name_en": "Kerman",
        "lat": 30.2839,
        "lon": 57.0834,
        "timezone": "Asia/Tehran"
    },
    "همدان": {
        "name_en": "Hamadan",
        "lat": 34.7992,
        "lon": 48.5146,
        "timezone": "Asia/Tehran"
    },
    "اراک": {
        "name_en": "Arak",
        "lat": 34.0917,
        "lon": 49.6892,
        "timezone": "Asia/Tehran"
    },
    "یزد": {
        "name_en": "Yazd",
        "lat": 31.8974,
        "lon": 54.3569,
        "timezone": "Asia/Tehran"
    },
    "اردبیل": {
        "name_en": "Ardabil",
        "lat": 38.2498,
        "lon": 48.2933,
        "timezone": "Asia/Tehran"
    },
    "بندرعباس": {
        "name_en": "Bandar Abbas",
        "lat": 27.1865,
        "lon": 56.2808,
        "timezone": "Asia/Tehran"
    },
    "قزوین": {
        "name_en": "Qazvin",
        "lat": 36.2688,
        "lon": 50.0041,
        "timezone": "Asia/Tehran"
    },
    "زنجان": {
        "name_en": "Zanjan",
        "lat": 36.6736,
        "lon": 48.4787,
        "timezone": "Asia/Tehran"
    },
    "سنندج": {
        "name_en": "Sanandaj",
        "lat": 35.3144,
        "lon": 46.9978,
        "timezone": "Asia/Tehran"
    },
    "خرم‌آباد": {
        "name_en": "Khorramabad",
        "lat": 33.4878,
        "lon": 48.3558,
        "timezone": "Asia/Tehran"
    },
    "گرگان": {
        "name_en": "Gorgan",
        "lat": 36.8427,
        "lon": 54.4441,
        "timezone": "Asia/Tehran"
    },
    "ساری": {
        "name_en": "Sari",
        "lat": 36.5633,
        "lon": 53.0601,
        "timezone": "Asia/Tehran"
    },
    "بوشهر": {
        "name_en": "Bushehr",
        "lat": 28.9684,
        "lon": 50.8385,
        "timezone": "Asia/Tehran"
    },
    "بیرجند": {
        "name_en": "Birjand",
        "lat": 32.8663,
        "lon": 59.2211,
        "timezone": "Asia/Tehran"
    },
    "سمنان": {
        "name_en": "Semnan",
        "lat": 35.5769,
        "lon": 53.3920,
        "timezone": "Asia/Tehran"
    },
    "یاسوج": {
        "name_en": "Yasuj",
        "lat": 30.6682,
        "lon": 51.5880,
        "timezone": "Asia/Tehran"
    },
    "ایلام": {
        "name_en": "Ilam",
        "lat": 33.6374,
        "lon": 46.4227,
        "timezone": "Asia/Tehran"
    },
    "شهرکرد": {
        "name_en": "Shahrekord",
        "lat": 32.3256,
        "lon": 50.8644,
        "timezone": "Asia/Tehran"
    }
}

def get_city_info(city_name):
    """
    Get city information by Persian name
    
    Args:
        city_name: Persian name of the city
        
    Returns:
        Dictionary with city info or None if not found
    """
    return IRANIAN_CITIES.get(city_name)

def get_all_cities():
    """
    Get list of all city names in Persian
    
    Returns:
        List of Persian city names
    """
    return sorted(IRANIAN_CITIES.keys())

def get_city_coordinates(city_name):
    """
    Get latitude and longitude for a city
    
    Args:
        city_name: Persian name of the city
        
    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    city = IRANIAN_CITIES.get(city_name)
    if city:
        return (city['lat'], city['lon'])
    return None
