# -*- coding: utf-8 -*-
"""
Chart Renderer - Creates visual astrology chart wheels
Similar to ZET software visualization
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from typing import Dict
import logging
from utils.geo_format import format_arc_dms

logger = logging.getLogger(__name__)

# Planet symbols (Unicode)
PLANET_SYMBOLS = {
    'Sun': '☉',
    'Moon': '☽',
    'Mercury': '☿',
    'Venus': '♀',
    'Mars': '♂',
    'Jupiter': '♃',
    'Saturn': '♄',
    'Uranus': '♅',
    'Neptune': '♆',
    'Pluto': '♇'
}

# Zodiac symbols
ZODIAC_SYMBOLS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']

# Element colors aligned with app UI (fire, earth, air, water × 3)
ZODIAC_ELEMENT_COLORS = [
    '#ff9a4d', '#d4b896', '#9ed4f5', '#4a9fd8',
    '#ff9a4d', '#d4b896', '#9ed4f5', '#4a9fd8',
    '#ff9a4d', '#d4b896', '#9ed4f5', '#4a9fd8',
]

SIGN_FA = [
    'حمل', 'ثور', 'جوزا', 'سرطان', 'اسد', 'سنبله',
    'میزان', 'عقرب', 'قوس', 'جدی', 'دلو', 'حوت',
]


class ChartRenderer:
    """Renders astrological charts as circular diagrams"""

    def __init__(self, chart_data: Dict, size: tuple = (9, 9)):
        self.chart_data = chart_data
        self.size = size
        self.fig = None
        self.ax = None

    def _setup_figure(self):
        """Setup matplotlib figure and axis"""
        self.fig, self.ax = plt.subplots(
            figsize=self.size,
            subplot_kw=dict(projection='polar'),
            facecolor='#f4f6f8',
        )
        self.ax.set_theta_zero_location('E')
        self.ax.set_theta_direction(-1)
        self.ax.set_ylim(0, 3.2)
        self.ax.axis('off')

    def _draw_center_disc(self):
        """Inner white disc and decorative rings"""
        theta = np.linspace(0, 2 * np.pi, 200)
        self.ax.fill_between(theta, 0, 0.85, color='#ffffff', alpha=1.0, zorder=1)
        self.ax.plot(theta, np.full_like(theta, 0.85), color='#bdc3c7', linewidth=0.8, zorder=2)
        self.ax.plot(theta, np.full_like(theta, 2.45), color='#95a5a6', linewidth=1.0, zorder=2)
        self.ax.plot(theta, np.full_like(theta, 3.0), color='#2c3e50', linewidth=2.0, zorder=3)

    def _draw_zodiac_wheel(self):
        """Draw the outer zodiac wheel"""
        houses = self.chart_data['houses']
        asc_longitude = houses['ascendant']['longitude']
        asc_sign_index = int(asc_longitude / 30)
        asc_degree_in_sign = asc_longitude % 30

        for i in range(12):
            zodiac_index = (asc_sign_index + i) % 12
            start_angle = np.radians(i * 30 - asc_degree_in_sign)
            end_angle = np.radians((i + 1) * 30 - asc_degree_in_sign)

            theta = np.linspace(start_angle, end_angle, 80)
            r_inner = 2.45
            r_outer = 3.0

            self.ax.fill_between(
                theta, r_inner, r_outer,
                color=ZODIAC_ELEMENT_COLORS[zodiac_index],
                alpha=0.55,
                zorder=4,
            )
            self.ax.plot(
                [start_angle, start_angle], [r_inner, r_outer],
                color='#2c3e50', linewidth=0.6, zorder=5,
            )

            mid_angle = np.radians(i * 30 + 15 - asc_degree_in_sign)
            self.ax.text(
                mid_angle, 2.72, ZODIAC_SYMBOLS[zodiac_index],
                ha='center', va='center', fontsize=14, weight='bold',
                color='#1a252f', zorder=6,
            )

        # Degree ticks every 10° on zodiac ring
        for deg in range(0, 360, 10):
            tick_angle = np.radians(deg - asc_degree_in_sign)
            self.ax.plot(
                [tick_angle, tick_angle], [2.38, 2.45],
                color='#7f8c8d', linewidth=0.4, zorder=5,
            )

    def _draw_houses(self):
        """Draw house cusps"""
        houses = self.chart_data['houses']
        asc_longitude = houses['ascendant']['longitude']

        for house in houses['cusps']:
            relative_longitude = (house['longitude'] - asc_longitude) % 360
            angle = np.radians(relative_longitude)

            self.ax.plot(
                [angle, angle], [0.85, 2.45],
                color='#3498db', linewidth=0.9, alpha=0.55, zorder=7,
            )

            house_num = house['house']
            next_house_idx = house_num % 12
            next_house = houses['cusps'][next_house_idx]
            next_relative = (next_house['longitude'] - asc_longitude) % 360

            if next_relative < relative_longitude:
                next_relative += 360
            mid_relative = (relative_longitude + next_relative) / 2
            if mid_relative >= 360:
                mid_relative -= 360
            mid_angle = np.radians(mid_relative)

            self.ax.text(
                mid_angle, 1.45, str(house_num),
                ha='center', va='center', fontsize=9, weight='bold',
                color='#2c3e50',
                bbox=dict(
                    boxstyle='circle', facecolor='#ecf0f1',
                    edgecolor='#95a5a6', alpha=0.95, pad=0.3,
                ),
                zorder=8,
            )

    def _draw_ascendant_mc(self):
        """Draw Ascendant, MC, IC, DSC lines"""
        houses = self.chart_data['houses']
        asc_longitude = houses['ascendant']['longitude']

        # ASC at East
        asc_angle = 0
        self.ax.plot([asc_angle, asc_angle], [0, 3.0], color='#e74c3c', linewidth=2.8, alpha=0.9, zorder=9)
        self.ax.text(asc_angle, 3.08, 'ASC', ha='center', va='bottom',
                     fontsize=11, weight='bold', color='#c0392b', zorder=10)

        # DSC opposite ASC
        dsc_angle = np.pi
        self.ax.plot([dsc_angle, dsc_angle], [0, 3.0], color='#e74c3c', linewidth=1.2, alpha=0.45, zorder=9)
        self.ax.text(dsc_angle, 3.08, 'DSC', ha='center', va='bottom',
                     fontsize=9, weight='bold', color='#c0392b', alpha=0.7, zorder=10)

        mc_relative = (houses['midheaven']['longitude'] - asc_longitude) % 360
        mc_angle = np.radians(mc_relative)
        self.ax.plot([mc_angle, mc_angle], [0, 3.0], color='#27ae60', linewidth=2.8, alpha=0.9, zorder=9)
        self.ax.text(mc_angle, 3.08, 'MC', ha='center', va='bottom',
                     fontsize=11, weight='bold', color='#1e8449', zorder=10)

        ic_relative = (mc_relative + 180) % 360
        ic_angle = np.radians(ic_relative)
        self.ax.plot([ic_angle, ic_angle], [0, 3.0], color='#27ae60', linewidth=1.2, alpha=0.45, zorder=9)
        self.ax.text(ic_angle, 3.08, 'IC', ha='center', va='bottom',
                     fontsize=9, weight='bold', color='#1e8449', alpha=0.7, zorder=10)

    def _draw_planets(self):
        """Draw planets on the chart with simple overlap offset"""
        planets = self.chart_data['planets']
        houses = self.chart_data['houses']
        asc_longitude = houses['ascendant']['longitude']

        planet_positions = []
        for name, data in planets.items():
            if data:
                relative_longitude = (data['longitude'] - asc_longitude) % 360
                angle = np.radians(relative_longitude)
                planet_positions.append((name, angle, data))

        planet_positions.sort(key=lambda x: x[1])

        # Stagger radius when planets are within ~8°
        used_angles = []
        for name, angle, data in planet_positions:
            radius = 2.05
            for prev in used_angles:
                if abs(angle - prev) < np.radians(8):
                    radius = 1.88 if radius == 2.05 else 2.05
                    break
            used_angles.append(angle)

            symbol = PLANET_SYMBOLS.get(name, name[0])
            is_retro = data['retrograde']
            color = '#c0392b' if is_retro else '#2c3e50'
            label = symbol + (' ℞' if is_retro else '')

            self.ax.text(
                angle, radius, label,
                ha='center', va='center', fontsize=12, weight='bold', color=color,
                bbox=dict(
                    boxstyle='round,pad=0.25', facecolor='#ffffff',
                    edgecolor=color, alpha=0.95, linewidth=1.2,
                ),
                zorder=11,
            )

            degree_text = format_arc_dms(data['degree_in_sign'])
            self.ax.text(
                angle, radius - 0.22, degree_text,
                ha='center', va='center', fontsize=6.5, color='#555555', zorder=11,
            )

    def _draw_nodes(self):
        """Draw lunar nodes"""
        nodes = self.chart_data.get('nodes')
        if not nodes:
            return

        houses = self.chart_data['houses']
        asc_longitude = houses['ascendant']['longitude']

        for key, symbol in (('north_node', '☊'), ('south_node', '☋')):
            node = nodes[key]
            relative = (node['longitude'] - asc_longitude) % 360
            angle = np.radians(relative)
            self.ax.text(
                angle, 2.05, symbol,
                ha='center', va='center', fontsize=12, weight='bold', color='#6c3483',
                bbox=dict(
                    boxstyle='round,pad=0.2', facecolor='#ffffff',
                    edgecolor='#8e44ad', alpha=0.95, linewidth=1.1,
                ),
                zorder=11,
            )

    def _chart_title(self) -> str:
        asc = self.chart_data['houses']['ascendant']
        sign_fa = asc.get('sign_fa', '')
        sect = 'روز' if self.chart_data.get('is_diurnal', True) else 'شب'
        if sign_fa:
            return f'زایچه تولد — طالع {sign_fa} — سکت {sect}'
        return 'زایچه تولد'

    def render(self) -> str:
        """Render the complete chart and return base64 PNG."""
        logger.info("Rendering astrological chart")

        self._setup_figure()
        self._draw_center_disc()
        self._draw_zodiac_wheel()
        self._draw_houses()
        self._draw_ascendant_mc()
        self._draw_planets()
        self._draw_nodes()

        self.fig.suptitle(
            self._chart_title(),
            fontsize=13, weight='bold', color='#2c3e50', y=0.97,
        )

        buffer = io.BytesIO()
        plt.savefig(
            buffer, format='png', dpi=180, bbox_inches='tight',
            facecolor=self.fig.get_facecolor(), edgecolor='none',
            pad_inches=0.15,
        )
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()

        plt.close(self.fig)
        logger.info("Chart rendered successfully")

        return image_base64

    def save(self, filename: str):
        """Save chart to file"""
        self._setup_figure()
        self._draw_center_disc()
        self._draw_zodiac_wheel()
        self._draw_houses()
        self._draw_ascendant_mc()
        self._draw_planets()
        self._draw_nodes()

        plt.savefig(
            filename, dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none',
        )
        plt.close(self.fig)
        logger.info(f"Chart saved to {filename}")


def create_chart_image(chart_data: Dict, size: tuple = (9, 9)) -> str:
    """Quick function to create chart image as base64 PNG."""
    renderer = ChartRenderer(chart_data, size=size)
    return renderer.render()
