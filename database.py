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


class StaleBirthChartError(RuntimeError):
    """A report or edit was based on an earlier version of the saved birth data."""


def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("BEGIN IMMEDIATE")

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
            solar_city TEXT,
            summary_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            api_key TEXT NOT NULL,
            base_url TEXT NOT NULL,
            model TEXT NOT NULL
        )
    """)

    columns = {row["name"] for row in cursor.execute("PRAGMA table_info(birth_charts)")}
    if "solar_city" not in columns:
        cursor.execute("ALTER TABLE birth_charts ADD COLUMN solar_city TEXT")
    if "summary_key" not in columns:
        cursor.execute("ALTER TABLE birth_charts ADD COLUMN summary_key TEXT")
    for column in ("revision", "analysis_revision"):
        if column not in columns:
            cursor.execute(f"ALTER TABLE birth_charts ADD COLUMN {column} INTEGER NOT NULL DEFAULT 0")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS birth_charts_summary_key ON birth_charts(summary_key)")
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def get_ai_settings():
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT api_key, base_url, model FROM ai_settings WHERE id = 1").fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()


def save_ai_settings(api_key, base_url, model):
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
                INSERT INTO ai_settings (id, api_key, base_url, model) VALUES (1, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    api_key = COALESCE(NULLIF(excluded.api_key, ''), ai_settings.api_key),
                    base_url = excluded.base_url,
                    model = excluded.model
            """, (api_key, base_url, model))
    finally:
        conn.close()


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
            astro_data, ai_analysis, vision, solar_city, summary_key
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(summary_key) DO UPDATE SET
            ai_analysis = excluded.ai_analysis, updated_at = CURRENT_TIMESTAMP
        WHERE birth_charts.revision = 0 AND NULLIF(TRIM(birth_charts.ai_analysis), '') IS NULL
            AND excluded.ai_analysis IS NOT NULL
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
        data.get('vision', ''),
        data.get('solar_city'),
        data.get('summary_key')
    ))

    chart_id = cursor.lastrowid
    if data.get('summary_key'):
        row = cursor.execute(
            "SELECT id, revision FROM birth_charts WHERE summary_key = ?", (data['summary_key'],)
        ).fetchone()
        if row['revision'] != 0 and data.get('ai_analysis'):
            conn.rollback()
            conn.close()
            raise StaleBirthChartError()
        chart_id = row['id']
    conn.commit()
    conn.close()
    
    logger.info(f"Saved birth chart with ID: {chart_id}")
    return chart_id


def get_birth_chart(chart_id):
    """Get birth chart by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT *, (revision = analysis_revision AND NULLIF(TRIM(ai_analysis), '') IS NOT NULL) AS has_analysis FROM birth_charts WHERE id = ?", (chart_id,))
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
        SELECT id, name, birth_date_persian, city_name, created_at,
               (revision = analysis_revision AND NULLIF(TRIM(ai_analysis), '') IS NOT NULL) AS has_analysis
        FROM birth_charts
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    
    charts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return charts


def update_birth_chart_analysis(chart_id, ai_analysis, *, revision, only_if_missing=False):
    """Save a structured report to an existing chart."""
    conn = get_db_connection()
    try:
        with conn:
            result = conn.execute("""
                UPDATE birth_charts
                SET ai_analysis = ?, analysis_revision = revision, summary_key = COALESCE(summary_key, LOWER(HEX(RANDOMBLOB(16)))),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND revision = ?
                  AND (NOT ? OR analysis_revision != revision OR NULLIF(TRIM(ai_analysis), '') IS NULL)
            """, (ai_analysis, chart_id, revision, only_if_missing))
            if result.rowcount == 0:
                row = conn.execute("SELECT revision FROM birth_charts WHERE id = ?", (chart_id,)).fetchone()
                if not row or row['revision'] != revision:
                    raise StaleBirthChartError()
    finally:
        conn.close()


def update_birth_details(chart_id, revision, birth):
    """Apply corrected inputs without attaching an older report to them."""
    conn = get_db_connection()
    try:
        with conn:
            result = conn.execute("""
                UPDATE birth_charts
                SET birth_date_persian = ?, birth_date_gregorian = ?,
                    birth_time_local = ?, birth_time_utc = ?, city_name = ?,
                    latitude = ?, longitude = ?, timezone = ?, solar_city = ?,
                    revision = revision + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND revision = ?
            """, (birth['jalali_date'], birth['gregorian_full'], birth['local_time'], birth['utc_time'],
                  birth['city_name'], birth['lat'], birth['lon'], birth['timezone'], birth['solar_city'],
                  chart_id, revision))
            if result.rowcount == 0:
                raise StaleBirthChartError()
    finally:
        conn.close()


def delete_birth_chart(chart_id):
    """Delete the saved birth data and analysis in the same row."""
    conn = get_db_connection()
    try:
        with conn:
            result = conn.execute("DELETE FROM birth_charts WHERE id = ?", (chart_id,))
        return result.rowcount > 0
    finally:
        conn.close()


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
