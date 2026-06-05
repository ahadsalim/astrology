from .iranian_cities import IRANIAN_CITIES, get_city_coordinates
from database import get_city_from_db, get_all_cities_from_db

def get_city_info(city_name):
    """Get city info from database (fallback to static data)"""
    city = get_city_from_db(city_name)
    if city:
        return city
    # Fallback to static data
    return IRANIAN_CITIES.get(city_name)

def get_all_cities():
    """Get all cities from database (fallback to static data)"""
    try:
        cities = get_all_cities_from_db()
        if cities:
            return cities
    except Exception:
        pass
    # Fallback to static data
    return sorted(IRANIAN_CITIES.keys())

__all__ = ['IRANIAN_CITIES', 'get_city_info', 'get_all_cities', 'get_city_coordinates']
