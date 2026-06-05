# -*- coding: utf-8 -*-
"""
Database module for SQLite operations
"""

import sqlite3
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = "nojoom.db"


def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create cities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_fa TEXT NOT NULL UNIQUE,
            name_en TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            timezone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create birth_charts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS birth_charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birth_date_persian TEXT NOT NULL,
            birth_date_gregorian TEXT NOT NULL,
            birth_time_local TEXT NOT NULL,
            birth_time_utc TEXT NOT NULL,
            city_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            timezone TEXT NOT NULL,
            astro_data TEXT,
            ai_analysis TEXT,
            vision TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def populate_cities():
    """Populate cities table with Iranian cities data"""
    from data.iranian_cities import IRANIAN_CITIES
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if cities already exist
    cursor.execute("SELECT COUNT(*) FROM cities")
    count = cursor.fetchone()[0]
    
    if count > 0:
        logger.info(f"Cities table already populated with {count} cities")
        conn.close()
        return
    
    # Insert cities
    for name_fa, info in IRANIAN_CITIES.items():
        cursor.execute("""
            INSERT INTO cities (name_fa, name_en, latitude, longitude, timezone)
            VALUES (?, ?, ?, ?, ?)
        """, (name_fa, info['name_en'], info['lat'], info['lon'], info['timezone']))
    
    conn.commit()
    conn.close()
    logger.info(f"Populated cities table with {len(IRANIAN_CITIES)} cities")


def get_city_from_db(city_name):
    """Get city information from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name_fa, name_en, latitude, longitude, timezone
        FROM cities
        WHERE name_fa = ?
    """, (city_name,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'name_fa': row[0],
            'name_en': row[1],
            'lat': row[2],
            'lon': row[3],
            'timezone': row[4]
        }
    return None


def get_all_cities_from_db():
    """Get all city names from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name_fa FROM cities ORDER BY name_fa")
    cities = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return cities


def save_birth_chart(data):
    """
    Save birth chart data to database
    
    Args:
        data: Dictionary containing all birth chart information
        
    Returns:
        ID of the saved record
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO birth_charts (
            name, birth_date_persian, birth_date_gregorian,
            birth_time_local, birth_time_utc, city_name,
            latitude, longitude, timezone,
            astro_data, ai_analysis, vision
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('name'),
        data.get('birth_date_persian'),
        data.get('birth_date_gregorian'),
        data.get('birth_time_local'),
        data.get('birth_time_utc'),
        data.get('city_name'),
        data.get('latitude'),
        data.get('longitude'),
        data.get('timezone'),
        data.get('astro_data'),
        data.get('ai_analysis'),
        data.get('vision', '')
    ))
    
    chart_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    logger.info(f"Saved birth chart with ID: {chart_id}")
    return chart_id


def get_birth_chart(chart_id):
    """Get birth chart by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM birth_charts WHERE id = ?", (chart_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_all_birth_charts(limit=100):
    """Get all birth charts (limited)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, birth_date_persian, city_name, created_at
        FROM birth_charts
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    charts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return charts


def update_birth_chart_analysis(chart_id, ai_analysis):
    """Update AI analysis for a birth chart"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE birth_charts
        SET ai_analysis = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (ai_analysis, chart_id))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Updated AI analysis for chart ID: {chart_id}")


def delete_birth_chart(chart_id):
    """Delete a birth chart"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM birth_charts WHERE id = ?", (chart_id,))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Deleted birth chart ID: {chart_id}")


# ============================================================================
# Cities Management Functions
# ============================================================================

def add_city(name_fa, name_en, latitude, longitude, timezone="Asia/Tehran"):
    """
    Add a new city to the database
    
    Args:
        name_fa: Persian name of the city
        name_en: English name of the city
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        timezone: Timezone (default: Asia/Tehran)
        
    Returns:
        ID of the added city or None if failed
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO cities (name_fa, name_en, latitude, longitude, timezone)
            VALUES (?, ?, ?, ?, ?)
        """, (name_fa, name_en, latitude, longitude, timezone))
        
        city_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Added city: {name_fa} (ID: {city_id})")
        return city_id
    except sqlite3.IntegrityError:
        logger.error(f"City {name_fa} already exists")
        return None
    except Exception as e:
        logger.error(f"Error adding city: {e}")
        return None


def update_city(city_id, name_fa=None, name_en=None, latitude=None, longitude=None, timezone=None):
    """
    Update city information
    
    Args:
        city_id: ID of the city to update
        name_fa: New Persian name (optional)
        name_en: New English name (optional)
        latitude: New latitude (optional)
        longitude: New longitude (optional)
        timezone: New timezone (optional)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically
        updates = []
        params = []
        
        if name_fa is not None:
            updates.append("name_fa = ?")
            params.append(name_fa)
        if name_en is not None:
            updates.append("name_en = ?")
            params.append(name_en)
        if latitude is not None:
            updates.append("latitude = ?")
            params.append(latitude)
        if longitude is not None:
            updates.append("longitude = ?")
            params.append(longitude)
        if timezone is not None:
            updates.append("timezone = ?")
            params.append(timezone)
        
        if not updates:
            return False
        
        params.append(city_id)
        query = f"UPDATE cities SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        logger.info(f"Updated city ID: {city_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating city: {e}")
        return False


def delete_city(city_id):
    """
    Delete a city from the database
    
    Args:
        city_id: ID of the city to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM cities WHERE id = ?", (city_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted city ID: {city_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting city: {e}")
        return False


def get_city_by_id(city_id):
    """Get city information by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name_fa, name_en, latitude, longitude, timezone
        FROM cities
        WHERE id = ?
    """, (city_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'name_fa': row[1],
            'name_en': row[2],
            'latitude': row[3],
            'longitude': row[4],
            'timezone': row[5]
        }
    return None


def get_all_cities_detailed():
    """Get all cities with full details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name_fa, name_en, latitude, longitude, timezone
        FROM cities
        ORDER BY name_fa
    """)
    
    cities = []
    for row in cursor.fetchall():
        cities.append({
            'id': row[0],
            'name_fa': row[1],
            'name_en': row[2],
            'latitude': row[3],
            'longitude': row[4],
            'timezone': row[5]
        })
    
    conn.close()
    return cities


# Initialize database on module import
try:
    init_database()
    populate_cities()
except Exception as e:
    logger.error(f"Error initializing database: {e}")
