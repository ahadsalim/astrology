# -*- coding: utf-8 -*-
"""Favicon, site name, and self-hosted Vazirmatn."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_FONT_HOSTS = (
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "cdn.jsdelivr.net",
    "fontlibrary.org",
)


class BrandingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app

        app.config.update(TESTING=True)
        cls.client = app.test_client()

    def test_favicon_ico_is_served_with_icon_type(self):
        response = self.client.get("/favicon.ico")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/vnd.microsoft.icon")
        self.assertTrue(response.data.startswith(b"\x00\x00\x01\x00"))

    def test_declared_icons_are_served(self):
        svg = self.client.get("/static/site-icon.svg")
        self.assertEqual(svg.status_code, 200)
        self.assertEqual(svg.mimetype, "image/svg+xml")
        self.assertIn(b"<svg", svg.data)

        apple = self.client.get("/static/apple-touch-icon.png")
        self.assertEqual(apple.status_code, 200)
        self.assertEqual(apple.mimetype, "image/png")
        self.assertTrue(apple.data.startswith(b"\x89PNG"))

    def test_variable_font_is_self_hosted(self):
        font = self.client.get("/static/fonts/Vazirmatn-Variable.woff2")
        self.assertEqual(font.status_code, 200)
        self.assertEqual(font.mimetype, "font/woff2")
        self.assertTrue(font.data.startswith(b"wOF2"))

        css = self.client.get("/static/fonts/vazirmatn.css")
        self.assertEqual(css.status_code, 200)
        body = css.get_data(as_text=True)
        self.assertIn('font-family: "Vazirmatn"', body)
        self.assertIn("font-display: swap", body)
        self.assertIn("Vazirmatn-Variable.woff2", body)
        for host in EXTERNAL_FONT_HOSTS:
            self.assertNotIn(host, body)

        license_file = self.client.get("/static/fonts/OFL.txt")
        self.assertEqual(license_file.status_code, 200)
        self.assertIn("SIL OPEN FONT LICENSE", license_file.get_data(as_text=True))

    def test_home_page_uses_new_name_and_no_remote_fonts(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("نجوم احکامی", html)
        self.assertNotIn("نجوم اطلس", html)
        self.assertIn('href="/favicon.ico"', html)
        self.assertIn("/static/fonts/vazirmatn.css", html)
        self.assertIn("/static/site-icon.svg", html)
        self.assertIn("/static/apple-touch-icon.png", html)
        for host in EXTERNAL_FONT_HOSTS:
            self.assertNotIn(host, html)

        style = self.client.get("/static/style.css")
        css = style.get_data(as_text=True)
        for host in EXTERNAL_FONT_HOSTS:
            self.assertNotIn(host, css)
        self.assertIn('"Vazirmatn", Tahoma, sans-serif', css)

    def test_old_site_name_is_gone_from_templates(self):
        for path in (ROOT / "templates").glob("*.html"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("نجوم اطلس", text, path.name)
            self.assertNotIn("Nojoom Atlas", text, path.name)

    def test_chart_labels_use_vazirmatn_files(self):
        from core.chart_renderer import ChartRenderer, shape_persian, vazir_font

        regular = vazir_font(12)
        bold = vazir_font(13, bold=True)
        self.assertTrue(regular.get_file().endswith("Vazirmatn-Regular.ttf"))
        self.assertTrue(bold.get_file().endswith("Vazirmatn-Bold.ttf"))
        self.assertNotEqual(shape_persian("حمل"), "حمل")

        cusps = [{"house": index + 1, "longitude": index * 30} for index in range(12)]
        chart = {
            "is_diurnal": True,
            "houses": {
                "ascendant": {"longitude": 10, "sign_fa": "حمل"},
                "midheaven": {"longitude": 100},
                "cusps": cusps,
            },
            "planets": {
                "Sun": {"longitude": 40, "retrograde": False, "degree_in_sign": 10.5},
            },
        }
        image = ChartRenderer(chart).render()
        self.assertGreater(len(image), 1000)


if __name__ == "__main__":
    unittest.main()
