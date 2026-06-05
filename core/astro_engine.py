# -*- coding: utf-8 -*-
"""
Astrology Engine - Professional Swiss Ephemeris Calculations
Similar to ZET software accuracy
"""

import swisseph as swe
import logging
from typing import Dict, List, Tuple
import math

from core.chart_conditions import enrich_aspect_record, get_sun_relation
from core.traditional_dignities import (
    chart_is_diurnal,
    get_dignity_fa,
    get_major_essential_dignity,
    get_minor_dignity_rulers,
)
from core.vedic_special_states import (
    format_vedic_special_states,
    get_vedic_special_states,
)

logger = logging.getLogger(__name__)

# Sidereal zodiac: Lahiri ayanamsa (common in Vedic / dual-zodiac charts)
SIDEREAL_AYANAMSA = swe.SIDM_LAHIRI

# Planet constants
PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO
}

# Persian planet names
PLANET_NAMES_FA = {
    'Sun': 'شمس',
    'Moon': 'قمر',
    'Mercury': 'عطارد',
    'Venus': 'زهره',
    'Mars': 'مریخ',
    'Jupiter': 'مشتری',
    'Saturn': 'زحل',
    'Uranus': 'اورانوس',
    'Neptune': 'نپتون',
    'Pluto': 'پلوتو'
}

# Zodiac signs
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer',
    'Leo', 'Virgo', 'Libra', 'Scorpio',
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

ZODIAC_SIGNS_FA = [
    'حمل', 'ثور', 'جوزا', 'سرطان',
    'اسد', 'سنبله', 'میزان', 'عقرب',
    'قوس', 'جدی', 'دلو', 'حوت'
]

# Aspect definitions (major aspects)
ASPECTS = {
    'Conjunction': {'angle': 0, 'orb': 8, 'symbol': '☌'},
    'Opposition': {'angle': 180, 'orb': 8, 'symbol': '☍'},
    'Trine': {'angle': 120, 'orb': 8, 'symbol': '△'},
    'Square': {'angle': 90, 'orb': 8, 'symbol': '□'},
    'Sextile': {'angle': 60, 'orb': 6, 'symbol': '⚹'}
}

ASPECTS_FA = {
    'Conjunction': 'اقتران',
    'Opposition': 'مقابله',
    'Trine': 'تثلیث',
    'Square': 'تربیع',
    'Sextile': 'تسدیس'
}

NODE_NAMES_FA = {
    'NorthNode': 'رأس',
    'SouthNode': 'ذنب'
}



class AstroEngine:
    """Professional astrology calculation engine using Swiss Ephemeris"""
    
    def __init__(self, ephemeris_path=None):
        """
        Initialize the astrology engine
        
        Args:
            ephemeris_path: Path to Swiss Ephemeris data files (optional)
        """
        if ephemeris_path:
            swe.set_ephe_path(ephemeris_path)
        
        logger.info("AstroEngine initialized")
    
    def calculate_planets(self, julian_day: float) -> Dict:
        """
        Calculate positions of all planets
        
        Args:
            julian_day: Julian Day Number (UT)
            
        Returns:
            Dictionary with planet data
        """
        planets_data = {}
        swe.set_sid_mode(SIDEREAL_AYANAMSA)
        
        for name, planet_id in PLANETS.items():
            try:
                # Calculate planet position
                # swe.calc_ut returns a tuple: (xx, ret_flag)
                # xx is array: [longitude, latitude, distance, speed_long, speed_lat, speed_dist]
                result = swe.calc_ut(julian_day, planet_id)
                sidereal_result = swe.calc_ut(julian_day, planet_id, swe.FLG_SIDEREAL)
                
                longitude = result[0][0]  # Tropical ecliptic longitude
                latitude = result[0][1]   # Ecliptic latitude
                distance = result[0][2]   # Distance from Earth (AU)
                speed = result[0][3]      # Speed in longitude (degrees/day)
                sidereal_longitude = sidereal_result[0][0] % 360
                
                # Determine zodiac sign (tropical)
                sign_num = int(longitude / 30) % 12
                degree_in_sign = longitude % 30
                sign_num_sidereal = int(sidereal_longitude / 30) % 12
                degree_in_sign_sidereal = sidereal_longitude % 30
                
                # Check if retrograde
                is_retrograde = speed < 0
                
                # Calculate essential dignity
                dignity = get_major_essential_dignity(name, sign_num, degree_in_sign)
                
                planets_data[name] = {
                    'longitude': longitude,
                    'sidereal_longitude': sidereal_longitude,
                    'latitude': latitude,
                    'distance': distance,
                    'speed': speed,
                    'retrograde': is_retrograde,
                    'sign': ZODIAC_SIGNS[sign_num],
                    'sign_fa': ZODIAC_SIGNS_FA[sign_num],
                    'sign_sidereal': ZODIAC_SIGNS[sign_num_sidereal],
                    'sign_fa_sidereal': ZODIAC_SIGNS_FA[sign_num_sidereal],
                    'degree_in_sign': degree_in_sign,
                    'degree_in_sign_sidereal': degree_in_sign_sidereal,
                    'name_fa': PLANET_NAMES_FA[name],
                    'dignity': dignity,
                    'dignity_fa': get_dignity_fa(dignity)
                }
                
                logger.debug(f"{name}: {longitude:.4f}° in {ZODIAC_SIGNS[sign_num]}")
                
            except Exception as e:
                logger.error(f"Error calculating {name}: {e}")
                planets_data[name] = None
        
        return planets_data
    
    def _apply_minor_dignities(self, point_data: Dict, is_diurnal: bool) -> None:
        """Attach triplicity, term, and face rulers for a chart point (tropical)."""
        longitude = point_data['longitude'] % 360
        sign_num = int(longitude // 30) % 12
        degree_in_sign = longitude % 30
        rulers = get_minor_dignity_rulers(
            sign_num,
            degree_in_sign,
            is_diurnal,
        )

        point_data['triplicity_ruler'] = rulers['triplicity']
        point_data['triplicity_ruler_fa'] = PLANET_NAMES_FA[rulers['triplicity']]
        point_data['triplicity_ruler_2'] = rulers['triplicity_2']
        point_data['triplicity_ruler_2_fa'] = PLANET_NAMES_FA[rulers['triplicity_2']]
        point_data['triplicity_participating'] = rulers['participating']
        point_data['triplicity_participating_fa'] = PLANET_NAMES_FA[rulers['participating']]
        point_data['term_ruler'] = rulers['term']
        point_data['term_ruler_fa'] = PLANET_NAMES_FA[rulers['term']]
        point_data['face_ruler'] = rulers['face']
        point_data['face_ruler_fa'] = PLANET_NAMES_FA[rulers['face']]

    def _apply_sun_relation(self, point_data: Dict, point_key: str, sun_lon: float) -> None:
        rel = get_sun_relation(point_key, point_data['longitude'], sun_lon)
        point_data['sun_relation'] = rel['sun_relation']
        point_data['sun_relation_fa'] = rel['sun_relation_fa']

    def _enrich_sun_relations(self, planets_data: Dict) -> None:
        sun_data = planets_data.get('Sun')
        if not sun_data:
            return
        sun_lon = sun_data['longitude']
        for planet_key, planet_data in planets_data.items():
            if planet_data:
                self._apply_sun_relation(planet_data, planet_key, sun_lon)

    def _enrich_minor_dignities(self, planets_data: Dict, is_diurnal: bool) -> None:
        """Attach triplicity, term, and face rulers for each planet position."""
        for planet_data in planets_data.values():
            if planet_data:
                self._apply_minor_dignities(planet_data, is_diurnal)

    def _apply_sidereal_vedic_fields(self, data: Dict, sidereal_longitude: float) -> None:
        """Add sidereal sign/degree and Vedic state labels to a chart point."""
        sidereal_longitude = sidereal_longitude % 360
        sign_sidereal = int(sidereal_longitude // 30) % 12
        data['sidereal_longitude'] = sidereal_longitude
        data['degree_in_sign_sidereal'] = sidereal_longitude % 30
        data['sign_sidereal'] = ZODIAC_SIGNS[sign_sidereal]
        data['sign_fa_sidereal'] = ZODIAC_SIGNS_FA[sign_sidereal]
        states = get_vedic_special_states(sidereal_longitude)
        data['vedic_states'] = states
        data['vedic_states_fa'] = format_vedic_special_states(sidereal_longitude)

    def _enrich_vedic_special_states(self, planets_data: Dict) -> None:
        """Attach Vedic special-degree states from sidereal (Lahiri) longitude."""
        for planet_data in planets_data.values():
            if not planet_data:
                continue
            sidereal_lon = planet_data.get('sidereal_longitude')
            if sidereal_lon is None:
                continue
            self._apply_sidereal_vedic_fields(planet_data, sidereal_lon)

    def _build_lunar_node_entry(
        self, name_fa: str, tropical_longitude: float, sidereal_longitude: float
    ) -> Dict:
        tropical_longitude = tropical_longitude % 360
        sign_num = int(tropical_longitude // 30) % 12
        data = {
            'longitude': tropical_longitude,
            'sign': ZODIAC_SIGNS[sign_num],
            'sign_fa': ZODIAC_SIGNS_FA[sign_num],
            'degree_in_sign': tropical_longitude % 30,
            'name_fa': name_fa,
        }
        self._apply_sidereal_vedic_fields(data, sidereal_longitude)
        return data
    
    def calculate_houses(self, julian_day: float, latitude: float, longitude: float, 
                        house_system: str = 'P') -> Dict:
        """
        Calculate house cusps and angles
        
        Args:
            julian_day: Julian Day Number
            latitude: Geographic latitude
            longitude: Geographic longitude
            house_system: House system code ('P' for Placidus, 'K' for Koch, etc.)
            
        Returns:
            Dictionary with houses and angles
        """
        try:
            # Calculate houses
            # Returns: (cusps[13], ascmc[10])
            # cusps[1-12] are house cusps, cusps[0] is unused
            # ascmc[0] = Ascendant, ascmc[1] = MC, ascmc[2] = ARMC, ascmc[3] = Vertex
            cusps, ascmc = swe.houses(julian_day, latitude, longitude, house_system.encode())
            
            # Extract important angles
            asc = ascmc[0]  # Ascendant
            mc = ascmc[1]   # Midheaven (Medium Coeli)
            
            # Determine signs for angles
            asc_sign = int(asc / 30)
            mc_sign = int(mc / 30)
            
            houses_data = {
                'system': house_system,
                'ascendant': {
                    'longitude': asc,
                    'sign': ZODIAC_SIGNS[asc_sign],
                    'sign_fa': ZODIAC_SIGNS_FA[asc_sign],
                    'degree_in_sign': asc % 30
                },
                'midheaven': {
                    'longitude': mc,
                    'sign': ZODIAC_SIGNS[mc_sign],
                    'sign_fa': ZODIAC_SIGNS_FA[mc_sign],
                    'degree_in_sign': mc % 30
                },
                'cusps': []
            }
            
            # Store house cusps (1-12)
            # Note: cusps tuple has indices 0-11 for houses 1-12
            for i in range(12):
                cusp_long = cusps[i]
                cusp_sign = int(cusp_long / 30)
                
                houses_data['cusps'].append({
                    'house': i + 1,  # House number 1-12
                    'longitude': cusp_long,
                    'sign': ZODIAC_SIGNS[cusp_sign],
                    'sign_fa': ZODIAC_SIGNS_FA[cusp_sign],
                    'degree_in_sign': cusp_long % 30
                })
            
            logger.info(f"Houses calculated: ASC={asc:.2f}°, MC={mc:.2f}°")
            return houses_data
            
        except Exception as e:
            logger.error(f"Error calculating houses: {e}")
            raise
    
    def calculate_lunar_nodes(self, julian_day: float) -> Dict:
        """
        Calculate North and South Lunar Nodes
        
        Args:
            julian_day: Julian Day Number
            
        Returns:
            Dictionary with node data
        """
        try:
            # Calculate True Node (more accurate than Mean Node)
            result = swe.calc_ut(julian_day, swe.TRUE_NODE)
            north_node = result[0][0]
            node_speed = result[0][3]
            is_retrograde = node_speed < 0

            swe.set_sid_mode(SIDEREAL_AYANAMSA)
            north_sidereal = swe.calc_ut(julian_day, swe.TRUE_NODE, swe.FLG_SIDEREAL)[0][0]
            south_node = (north_node + 180) % 360
            south_sidereal = (north_sidereal + 180) % 360

            north_entry = self._build_lunar_node_entry('رأس', north_node, north_sidereal)
            south_entry = self._build_lunar_node_entry('ذنب', south_node, south_sidereal)
            for entry, node_key in (
                (north_entry, 'NorthNode'),
                (south_entry, 'SouthNode'),
            ):
                entry['speed'] = node_speed
                entry['retrograde'] = is_retrograde
                sign_num = int(entry['longitude'] // 30) % 12
                dignity = get_major_essential_dignity(
                    node_key, sign_num, entry['degree_in_sign']
                )
                entry['dignity'] = dignity
                entry['dignity_fa'] = get_dignity_fa(dignity)

            return {
                'north_node': north_entry,
                'south_node': south_entry,
            }
            
        except Exception as e:
            logger.error(f"Error calculating lunar nodes: {e}")
            return None
    
    def determine_planet_house(self, planet_longitude: float, house_cusps: List) -> int:
        """
        Determine which house a planet is in
        
        Args:
            planet_longitude: Planet's ecliptic longitude
            house_cusps: List of house cusp data
            
        Returns:
            House number (1-12)
        """
        # Normalize longitude to 0-360
        planet_long = planet_longitude % 360
        
        for i in range(12):
            cusp1 = house_cusps[i]['longitude']
            cusp2 = house_cusps[(i + 1) % 12]['longitude']
            
            # Handle wrap-around at 360/0 degrees
            if cusp2 < cusp1:
                cusp2 += 360
                if planet_long < cusp1:
                    planet_long += 360
            
            if cusp1 <= planet_long < cusp2:
                return i + 1
        
        return 1  # Default to first house if calculation fails
    
    def calculate_aspects(self, planets_data: Dict, nodes_data: Dict = None) -> List[Dict]:
        """
        Calculate aspects between planets and optional lunar nodes
        
        Args:
            planets_data: Dictionary of planet positions
            nodes_data: Optional dictionary of lunar nodes data
            
        Returns:
            List of aspect data
        """
        aspects_list = []

        # Build aspect points using planets and optional lunar nodes
        aspect_points = {}
        for planet_name, planet_data in planets_data.items():
            if planet_data:
                aspect_points[planet_name] = {
                    'longitude': planet_data['longitude'],
                    'speed': planet_data.get('speed', 0.0),
                    'name_fa': PLANET_NAMES_FA[planet_name],
                }

        if nodes_data:
            north_node = nodes_data.get('north_node')
            south_node = nodes_data.get('south_node')

            if north_node:
                aspect_points['NorthNode'] = {
                    'longitude': north_node['longitude'],
                    'speed': north_node.get('speed', 0.0),
                    'name_fa': NODE_NAMES_FA['NorthNode'],
                }

            if south_node:
                aspect_points['SouthNode'] = {
                    'longitude': south_node['longitude'],
                    'speed': south_node.get('speed', 0.0),
                    'name_fa': NODE_NAMES_FA['SouthNode'],
                }

        point_names = list(aspect_points.keys())
        
        for i, point1 in enumerate(point_names):
            for point2 in point_names[i+1:]:
                # Exclude the always-opposite North/South Node pair.
                if {point1, point2} == {'NorthNode', 'SouthNode'}:
                    continue

                p1 = aspect_points[point1]
                p2 = aspect_points[point2]
                long1 = p1['longitude']
                long2 = p2['longitude']
                speed1 = p1.get('speed', 0.0)
                speed2 = p2.get('speed', 0.0)

                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff

                for aspect_name, aspect_data in ASPECTS.items():
                    target_angle = aspect_data['angle']
                    orb = aspect_data['orb']

                    if abs(diff - target_angle) <= orb:
                        aspect_entry = {
                            'planet1': point1,
                            'planet1_fa': p1['name_fa'],
                            'planet2': point2,
                            'planet2_fa': p2['name_fa'],
                            'aspect': aspect_name,
                            'aspect_fa': ASPECTS_FA[aspect_name],
                            'symbol': aspect_data['symbol'],
                            'angle': diff,
                            'orb': abs(diff - target_angle),
                            'exact': abs(diff - target_angle) < 1,
                        }
                        enrich_aspect_record(
                            aspect_entry,
                            lon1=long1,
                            lon2=long2,
                            speed1=speed1,
                            speed2=speed2,
                            name1_fa=p1['name_fa'],
                            name2_fa=p2['name_fa'],
                            target_angle=target_angle,
                            aspect_name=aspect_name,
                        )
                        aspects_list.append(aspect_entry)
        
        # Sort by orb (exact aspects first)
        aspects_list.sort(key=lambda x: x['orb'])
        
        logger.info(f"Found {len(aspects_list)} aspects")
        return aspects_list
    
    def calculate_transits(self, julian_day_now: float, natal_houses: Dict) -> Dict:
        """
        Calculate current transits (slow planets positions)
        
        Args:
            julian_day_now: Current Julian Day
            natal_houses: Natal chart houses data
            
        Returns:
            Dictionary with transit data
        """
        # Slow moving planets for transits
        transit_planets = {
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Uranus': swe.URANUS,
            'Neptune': swe.NEPTUNE,
            'Pluto': swe.PLUTO
        }
        
        transits_data = {}
        
        for name, planet_id in transit_planets.items():
            try:
                result = swe.calc_ut(julian_day_now, planet_id)
                longitude = result[0][0]
                speed = result[0][3]
                
                # Determine zodiac sign
                sign_num = int(longitude / 30)
                degree_in_sign = longitude % 30
                
                # Determine which natal house this transit is in
                house_num = self._find_house_for_longitude(longitude, natal_houses)
                
                transits_data[name] = {
                    'longitude': longitude,
                    'speed': speed,
                    'retrograde': speed < 0,
                    'sign': ZODIAC_SIGNS[sign_num],
                    'sign_fa': ZODIAC_SIGNS_FA[sign_num],
                    'degree_in_sign': degree_in_sign,
                    'name_fa': PLANET_NAMES_FA[name],
                    'natal_house': house_num
                }
                
            except Exception as e:
                logger.error(f"Error calculating transit for {name}: {e}")
                transits_data[name] = None
        
        return transits_data

    TRANSIT_SLOW_ORDER = ('Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto')
    TRANSIT_FAST_ORDER = ('Sun', 'Moon', 'Mercury', 'Venus', 'Mars')

    def _transit_body_at_jd(self, julian_day: float, planet_id: int, name: str,
                            natal_houses: Dict) -> Dict:
        """Single transiting body position relative to natal houses."""
        result = swe.calc_ut(julian_day, planet_id)
        longitude = result[0][0]
        speed = result[0][3]
        sign_num = int(longitude / 30)
        degree_in_sign = longitude % 30
        house_num = self._find_house_for_longitude(longitude, natal_houses)
        return {
            'longitude': longitude,
            'speed': speed,
            'retrograde': speed < 0,
            'sign': ZODIAC_SIGNS[sign_num],
            'sign_fa': ZODIAC_SIGNS_FA[sign_num],
            'degree_in_sign': degree_in_sign,
            'name_fa': PLANET_NAMES_FA[name],
            'natal_house': house_num,
            'category': 'slow' if name in self.TRANSIT_SLOW_ORDER else 'fast',
        }

    def calculate_full_transits(self, julian_day_now: float, natal_houses: Dict) -> Dict:
        """
        Full moment transits: slow planets first, then personal planets, then nodes.
        """
        slow = {}
        for name in self.TRANSIT_SLOW_ORDER:
            try:
                slow[name] = self._transit_body_at_jd(
                    julian_day_now, PLANETS[name], name, natal_houses
                )
            except Exception as e:
                logger.error(f"Error calculating full transit for {name}: {e}")
                slow[name] = None

        fast = {}
        for name in self.TRANSIT_FAST_ORDER:
            try:
                fast[name] = self._transit_body_at_jd(
                    julian_day_now, PLANETS[name], name, natal_houses
                )
            except Exception as e:
                logger.error(f"Error calculating full transit for {name}: {e}")
                fast[name] = None

        nodes = {}
        try:
            nn = swe.calc_ut(julian_day_now, swe.TRUE_NODE)
            sn_lon = (nn[0][0] + 180) % 360
            nn_lon = nn[0][0]
            nn_speed = nn[0][3]
            for key, lon, speed, label in (
                ('north_node', nn_lon, nn_speed, 'رأس'),
                ('south_node', sn_lon, -nn_speed, 'ذنب'),
            ):
                sign_num = int(lon / 30)
                nodes[key] = {
                    'longitude': lon,
                    'speed': speed,
                    'retrograde': speed < 0,
                    'sign': ZODIAC_SIGNS[sign_num],
                    'sign_fa': ZODIAC_SIGNS_FA[sign_num],
                    'degree_in_sign': lon % 30,
                    'name_fa': label,
                    'natal_house': self._find_house_for_longitude(lon, natal_houses),
                    'category': 'node',
                }
        except Exception as e:
            logger.error(f"Error calculating transit nodes: {e}")

        return {'slow': slow, 'fast': fast, 'nodes': nodes}

    def calculate_transit_to_natal_aspects(
        self, julian_day_now: float, natal_chart_data: Dict
    ) -> List[Dict]:
        """Aspects between transiting sky at jd_now and natal chart points."""
        natal_houses = natal_chart_data['houses']
        transits = self.calculate_full_transits(julian_day_now, natal_houses)

        transit_points = {}
        for group in (transits['slow'], transits['fast']):
            for name, data in group.items():
                if data:
                    transit_points[f"tr_{name}"] = {
                        'longitude': data['longitude'],
                        'speed': data['speed'],
                        'name_fa': f"ترانزیت {data['name_fa']}",
                    }
        for key, data in transits.get('nodes', {}).items():
            if data:
                transit_points[f"tr_{key}"] = {
                    'longitude': data['longitude'],
                    'speed': data['speed'],
                    'name_fa': f"ترانزیت {data['name_fa']}",
                }

        natal_points = {}
        for name, data in natal_chart_data.get('planets', {}).items():
            if data:
                natal_points[f"na_{name}"] = {
                    'longitude': data['longitude'],
                    'speed': 0.0,
                    'name_fa': f"تولد {data['name_fa']}",
                }
        if natal_chart_data.get('nodes'):
            for key, node_key, label in (
                ('na_north', 'north_node', 'رأس'),
                ('na_south', 'south_node', 'ذنب'),
            ):
                node = natal_chart_data['nodes'].get(node_key)
                if node:
                    natal_points[key] = {
                        'longitude': node['longitude'],
                        'speed': 0.0,
                        'name_fa': f"تولد {label}",
                    }
        asc = natal_houses.get('ascendant')
        mc = natal_houses.get('midheaven')
        if asc:
            natal_points['na_asc'] = {
                'longitude': asc['longitude'],
                'speed': 0.0,
                'name_fa': 'تولد طالع',
            }
        if mc:
            natal_points['na_mc'] = {
                'longitude': mc['longitude'],
                'speed': 0.0,
                'name_fa': 'تولد قله آسمان',
            }

        aspects_list = []
        for tr_key, tr in transit_points.items():
            for na_key, na in natal_points.items():
                long1 = tr['longitude']
                long2 = na['longitude']
                speed1 = tr['speed']
                speed2 = na['speed']
                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff
                for aspect_name, aspect_data in ASPECTS.items():
                    target_angle = aspect_data['angle']
                    orb = aspect_data['orb']
                    if abs(diff - target_angle) <= orb:
                        aspect_entry = {
                            'planet1': tr_key,
                            'planet1_fa': tr['name_fa'],
                            'planet2': na_key,
                            'planet2_fa': na['name_fa'],
                            'aspect': aspect_name,
                            'aspect_fa': ASPECTS_FA[aspect_name],
                            'symbol': aspect_data['symbol'],
                            'angle': diff,
                            'orb': abs(diff - target_angle),
                            'exact': abs(diff - target_angle) < 1,
                        }
                        enrich_aspect_record(
                            aspect_entry,
                            lon1=long1,
                            lon2=long2,
                            speed1=speed1,
                            speed2=speed2,
                            name1_fa=tr['name_fa'],
                            name2_fa=na['name_fa'],
                            target_angle=target_angle,
                            aspect_name=aspect_name,
                        )
                        aspects_list.append(aspect_entry)

        aspects_list.sort(key=lambda x: x['orb'])
        logger.info(f"Found {len(aspects_list)} transit-to-natal aspects")
        return aspects_list
    
    def _find_house_for_longitude(self, longitude: float, houses_data: Dict) -> int:
        """
        Find which house a given longitude falls into
        
        Args:
            longitude: Ecliptic longitude (0-360)
            houses_data: Houses data with cusps
            
        Returns:
            House number (1-12)
        """
        cusps = houses_data['cusps']
        
        for i in range(len(cusps)):
            current_cusp = cusps[i]['longitude']
            next_cusp = cusps[(i + 1) % 12]['longitude']
            
            # Handle wrap-around at 0/360 degrees
            if next_cusp < current_cusp:
                if longitude >= current_cusp or longitude < next_cusp:
                    return cusps[i]['house']
            else:
                if current_cusp <= longitude < next_cusp:
                    return cusps[i]['house']
        
        return 1  # Default to house 1 if not found
    
    def calculate_solar_return(self, birth_jd: float, birth_month: int, birth_day: int, 
                              current_year: int, solar_lat: float, solar_lon: float) -> Dict:
        """
        Calculate Solar Return chart (when Sun returns to natal position)
        
        Args:
            birth_jd: Birth Julian Day
            birth_month: Birth month
            birth_day: Birth day
            current_year: Current year for solar return
            solar_lat: Latitude where person will be on birthday
            solar_lon: Longitude where person will be on birthday
            
        Returns:
            Dictionary with solar return chart data
        """
        try:
            # Get natal Sun position
            natal_sun = swe.calc_ut(birth_jd, swe.SUN)
            natal_sun_lon = natal_sun[0][0]
            
            logger.info(f"Calculating Solar Return for year {current_year}, natal Sun at {natal_sun_lon:.2f}°")
            
            # Approximate Julian Day for birthday in current year
            approx_jd = swe.julday(current_year, birth_month, birth_day, 12.0)
            
            # Use binary search to find exact moment (within 1 day range)
            # Sun moves about 1 degree per day, so search within +/- 1 day
            start_jd = approx_jd - 1.0
            end_jd = approx_jd + 1.0
            
            # Binary search for exact moment
            tolerance = 0.01  # 0.01 degrees tolerance
            max_iterations = 20
            
            for iteration in range(max_iterations):
                mid_jd = (start_jd + end_jd) / 2.0
                current_sun = swe.calc_ut(mid_jd, swe.SUN)
                current_sun_lon = current_sun[0][0]
                
                # Calculate difference (handle wrap-around at 0/360)
                diff = current_sun_lon - natal_sun_lon
                if diff > 180:
                    diff -= 360
                elif diff < -180:
                    diff += 360
                
                # Check if we found it
                if abs(diff) < tolerance:
                    solar_jd = mid_jd
                    logger.info(f"Solar Return found at JD {solar_jd:.4f}, Sun at {current_sun_lon:.2f}°")
                    
                    # Calculate houses for solar return location
                    houses, ascmc = swe.houses(solar_jd, solar_lat, solar_lon, b'P')
                    
                    # Calculate planets for solar return
                    sr_planets = {}
                    for name, planet_id in PLANETS.items():
                        result = swe.calc_ut(solar_jd, planet_id)
                        longitude = result[0][0]
                        sign_num = int(longitude / 30)
                        degree_in_sign = longitude % 30
                        
                        sr_planets[name] = {
                            'longitude': longitude,
                            'sign': ZODIAC_SIGNS[sign_num],
                            'sign_fa': ZODIAC_SIGNS_FA[sign_num],
                            'degree_in_sign': degree_in_sign,
                            'name_fa': PLANET_NAMES_FA[name]
                        }
                    
                    # Solar return angles
                    sr_angles = {
                        'asc': {
                            'longitude': ascmc[0],
                            'sign': ZODIAC_SIGNS[int(ascmc[0] / 30)],
                            'sign_fa': ZODIAC_SIGNS_FA[int(ascmc[0] / 30)],
                            'degree_in_sign': ascmc[0] % 30
                        },
                        'mc': {
                            'longitude': ascmc[1],
                            'sign': ZODIAC_SIGNS[int(ascmc[1] / 30)],
                            'sign_fa': ZODIAC_SIGNS_FA[int(ascmc[1] / 30)],
                            'degree_in_sign': ascmc[1] % 30
                        }
                    }
                    
                    return {
                        'julian_day': solar_jd,
                        'planets': sr_planets,
                        'angles': sr_angles,
                        'natal_sun_position': natal_sun_lon
                    }
                
                # Adjust search range
                if diff < 0:
                    start_jd = mid_jd
                else:
                    end_jd = mid_jd
            
            logger.warning(f"Could not find exact solar return moment after {max_iterations} iterations")
            return None
            
        except Exception as e:
            logger.error(f"Error calculating solar return: {e}", exc_info=True)
            return None
    
    def calculate_complete_chart(self, julian_day: float, latitude: float, 
                                 longitude: float, house_system: str = 'P') -> Dict:
        """
        Calculate complete astrological chart
        
        Args:
            julian_day: Julian Day Number
            latitude: Geographic latitude
            longitude: Geographic longitude
            house_system: House system code
            
        Returns:
            Complete chart data
        """
        logger.info(f"Calculating chart for JD={julian_day}, Lat={latitude}, Lon={longitude}")
        
        # Calculate all components
        planets = self.calculate_planets(julian_day)
        houses = self.calculate_houses(julian_day, latitude, longitude, house_system)
        nodes = self.calculate_lunar_nodes(julian_day)
        aspects = self.calculate_aspects(planets, nodes)
        
        # Determine house positions for planets
        for planet_name, planet_data in planets.items():
            if planet_data:
                house_num = self.determine_planet_house(
                    planet_data['longitude'],
                    houses['cusps']
                )
                planet_data['house'] = house_num

        if nodes:
            for node_key in ('north_node', 'south_node'):
                node_data = nodes.get(node_key)
                if node_data:
                    node_data['house'] = self.determine_planet_house(
                        node_data['longitude'],
                        houses['cusps'],
                    )

        sun_house = planets.get('Sun', {}).get('house', 1) if planets.get('Sun') else 1
        is_diurnal = chart_is_diurnal(sun_house)
        self._enrich_minor_dignities(planets, is_diurnal)
        self._enrich_sun_relations(planets)
        self._enrich_vedic_special_states(planets)
        if nodes:
            sun_lon = planets.get('Sun', {}).get('longitude', 0.0)
            for node_key, node_id in (
                ('north_node', 'NorthNode'),
                ('south_node', 'SouthNode'),
            ):
                node_data = nodes.get(node_key)
                if node_data:
                    self._apply_minor_dignities(node_data, is_diurnal)
                    self._apply_sun_relation(node_data, node_id, sun_lon)

        swe.set_sid_mode(SIDEREAL_AYANAMSA)
        ayanamsa = swe.get_ayanamsa_ut(julian_day)
        for angle_key in ('ascendant', 'midheaven'):
            angle_data = houses[angle_key]
            sidereal_lon = (angle_data['longitude'] - ayanamsa) % 360
            self._apply_sidereal_vedic_fields(angle_data, sidereal_lon)
        
        chart_data = {
            'planets': planets,
            'houses': houses,
            'nodes': nodes,
            'aspects': aspects,
            'is_diurnal': is_diurnal,
            'sect_fa': 'روزانه' if is_diurnal else 'شبانه',
            'julian_day': julian_day,
            'coordinates': {
                'latitude': latitude,
                'longitude': longitude
            }
        }
        
        logger.info("Chart calculation complete")
        return chart_data
    
    def close(self):
        """Clean up Swiss Ephemeris resources"""
        swe.close()
        logger.info("AstroEngine closed")
