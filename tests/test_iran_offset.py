# -*- coding: utf-8 -*-
"""Iran birth-time offset: one Solar Hijri table, compared with pytz Asia/Tehran."""

import unittest
from datetime import datetime, timedelta

import jdatetime
import pytz
import swisseph as swe

# Import the application package the same way app.py does, so core's
# package init finishes before utils asks it for chart helpers.
import utils  # noqa: F401
from core.date_utils import DateTimeConverter
from core.iran_dst_history import (
    TZDATA_DISAGREEMENTS,
    get_dst_info,
    iran_offset_for_jalali,
    is_dst_active_in_year,
    should_apply_dst,
)

TEHRAN = pytz.timezone("Asia/Tehran")


def offset_of(jalali, hm):
    year, month, day = jalali
    hour, minute = hm
    return iran_offset_for_jalali(year, month, day, hour, minute)


def pytz_offset(jalali, hm=(12, 0)):
    year, month, day = jalali
    hour, minute = hm
    gregorian = jdatetime.date(year, month, day).togregorian()
    naive = datetime(gregorian.year, gregorian.month, gregorian.day, hour, minute)
    aware = TEHRAN.localize(naive, is_dst=None)
    return aware.utcoffset()


class IranOffsetTableTests(unittest.TestCase):
    """Every rule period, at a quiet midday and on the named edges."""

    def assertOffset(self, jalali, hm, expected, status="unique", dst=None):
        info = offset_of(jalali, hm)
        self.assertEqual(info["offset_str"], expected, info["rule"])
        self.assertEqual(info["local_time_status"], status, info["resolution"])
        if dst is not None:
            self.assertEqual(info["dst_applied"], dst)
        return info

    def test_before_10_aban_1356_is_0330(self):
        self.assertOffset((1300, 1, 1), (12, 0), "+03:30", dst=False)
        self.assertOffset((1350, 4, 15), (12, 0), "+03:30", dst=False)
        self.assertOffset((1356, 1, 1), (12, 0), "+03:30", dst=False)
        self.assertOffset((1356, 4, 15), (12, 0), "+03:30", dst=False)
        self.assertOffset((1356, 6, 31), (12, 0), "+03:30", dst=False)
        self.assertOffset((1356, 8, 9), (23, 59), "+03:30", dst=False)

    def test_10_aban_1356_moves_base_offset_to_0400(self):
        # 00:00–00:29 never happened; the clock jumped forward 30 minutes.
        gap = self.assertOffset((1356, 8, 10), (0, 0), "+04:00", status="nonexistent", dst=False)
        self.assertIn("post-transition", gap["resolution"])
        self.assertOffset((1356, 8, 10), (0, 29), "+04:00", status="nonexistent", dst=False)
        self.assertOffset((1356, 8, 10), (0, 30), "+04:00", status="unique", dst=False)
        self.assertOffset((1356, 8, 10), (12, 0), "+04:00", dst=False)
        self.assertOffset((1356, 10, 1), (12, 0), "+04:00", dst=False)
        self.assertOffset((1356, 12, 29), (23, 59), "+04:00", dst=False)

    def test_spring_and_autumn_1357_use_0500_then_0400(self):
        gap = self.assertOffset((1357, 1, 1), (0, 30), "+05:00", status="nonexistent", dst=True)
        self.assertIn("post-transition", gap["resolution"])
        self.assertOffset((1357, 1, 1), (1, 0), "+05:00", dst=True)
        self.assertOffset((1357, 1, 3), (12, 0), "+05:00", dst=True)
        self.assertOffset((1357, 4, 15), (12, 0), "+05:00", dst=True)
        self.assertOffset((1357, 6, 31), (22, 59), "+05:00", dst=True)
        overlap = self.assertOffset(
            (1357, 6, 31), (23, 30), "+05:00", status="ambiguous", dst=True
        )
        self.assertIn("earlier", overlap["resolution"])
        self.assertOffset((1357, 7, 1), (0, 0), "+04:00", dst=False)
        self.assertOffset((1357, 9, 15), (12, 0), "+04:00", dst=False)
        self.assertOffset((1357, 10, 9), (23, 29), "+04:00", dst=False)

    def test_10_dey_1357_returns_standard_offset_to_0330(self):
        overlap = self.assertOffset(
            (1357, 10, 9), (23, 45), "+04:00", status="ambiguous", dst=False
        )
        self.assertIn("earlier", overlap["resolution"])
        self.assertOffset((1357, 10, 10), (0, 0), "+03:30", dst=False)
        self.assertOffset((1357, 10, 10), (12, 0), "+03:30", dst=False)
        self.assertOffset((1357, 12, 15), (12, 0), "+03:30", dst=False)

    def test_1358_and_1359_first_half_daylight(self):
        for year in (1358, 1359):
            self.assertOffset((year, 1, 1), (0, 15), "+04:30", status="nonexistent", dst=True)
            self.assertOffset((year, 1, 1), (1, 0), "+04:30", dst=True)
            self.assertOffset((year, 4, 15), (12, 0), "+04:30", dst=True)
            self.assertOffset((year, 6, 31), (23, 30), "+04:30", status="ambiguous", dst=True)
            self.assertOffset((year, 7, 1), (0, 0), "+03:30", dst=False)
            self.assertOffset((year, 10, 1), (12, 0), "+03:30", dst=False)

    def test_1360_through_1370_have_no_daylight_time(self):
        self.assertOffset((1360, 1, 1), (0, 30), "+03:30", dst=False)
        self.assertOffset((1360, 4, 15), (12, 0), "+03:30", dst=False)
        self.assertOffset((1365, 4, 15), (12, 0), "+03:30", dst=False)
        self.assertOffset((1370, 1, 1), (12, 0), "+03:30", dst=False)
        self.assertOffset((1370, 4, 15), (12, 0), "+03:30", dst=False)
        self.assertOffset((1370, 6, 31), (23, 30), "+03:30", dst=False)

    def test_1371_through_1384_first_half_daylight(self):
        for year in (1371, 1380, 1384):
            self.assertOffset((year, 1, 1), (0, 30), "+04:30", status="nonexistent", dst=True)
            self.assertOffset((year, 4, 15), (12, 0), "+04:30", dst=True)
            self.assertOffset((year, 6, 31), (12, 0), "+04:30", dst=True)
            self.assertOffset((year, 6, 31), (23, 0), "+04:30", status="ambiguous", dst=True)
            self.assertOffset((year, 7, 1), (12, 0), "+03:30", dst=False)

    def test_1385_and_1386_have_no_daylight_time(self):
        for year in (1385, 1386):
            self.assertOffset((year, 1, 1), (0, 30), "+03:30", dst=False)
            self.assertOffset((year, 4, 15), (12, 0), "+03:30", dst=False)
            self.assertOffset((year, 6, 31), (23, 30), "+03:30", dst=False)

    def test_1387_through_1401_first_half_daylight(self):
        for year in (1387, 1390, 1401):
            self.assertOffset((year, 1, 1), (12, 0), "+04:30", dst=True)
            self.assertOffset((year, 4, 15), (12, 0), "+04:30", dst=True)
            self.assertOffset((year, 6, 31), (23, 59), "+04:30", status="ambiguous", dst=True)
            self.assertOffset((year, 7, 1), (0, 0), "+03:30", dst=False)
            self.assertOffset((year, 10, 1), (12, 0), "+03:30", dst=False)

    def test_from_1402_there_is_no_daylight_time(self):
        self.assertOffset((1402, 1, 1), (0, 0), "+03:30", dst=False)
        self.assertOffset((1402, 4, 15), (12, 0), "+03:30", dst=False)
        self.assertOffset((1402, 6, 31), (23, 30), "+03:30", dst=False)
        self.assertOffset((1404, 4, 1), (8, 15), "+03:30", dst=False)

    def test_invalid_clock_or_date_is_rejected(self):
        with self.assertRaises(ValueError):
            iran_offset_for_jalali(1390, 4, 15, 24, 0)
        with self.assertRaises(ValueError):
            iran_offset_for_jalali(1390, 12, 31, 12, 0)


class BirthTimeConversionTests(unittest.TestCase):
    """The chart path subtracts this offset and builds the Julian day from UTC."""

    def convert(self, jalali, hm):
        year, month, day = jalali
        hour, minute = hm
        text = f"{year:04d}-{month:02d}-{day:02d}"
        clock = f"{hour:02d}:{minute:02d}"
        return DateTimeConverter.parse_and_convert(text, clock)

    def assertUtc(self, jalali, hm, gregorian, utc, offset, status="unique"):
        result = self.convert(jalali, hm)
        self.assertEqual(result["gregorian_str"], gregorian)
        self.assertEqual(result["utc_time"], utc)
        self.assertEqual(result["utc_offset"], offset)
        self.assertEqual(result["local_time_status"], status)
        utc_dt = result["utc_datetime"]
        hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        expected_jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)
        self.assertAlmostEqual(result["julian_day"], expected_jd, places=7)
        return result

    def test_requested_period_samples_reach_utc(self):
        # 1365 summer used to be treated as +04:30 (07:30 UTC). It is +03:30.
        self.assertUtc((1365, 4, 15), (12, 0), "1986-07-06", "08:30", "+03:30")
        # 1357 summer used to be +04:30 (07:30 UTC). The +04:00 base plus one hour is +05:00.
        self.assertUtc((1357, 4, 15), (12, 0), "1978-07-06", "07:00", "+05:00")
        # 9 Aban is still +03:30; 10 Aban is the first +04:00 civil day.
        self.assertUtc((1356, 8, 9), (12, 0), "1977-10-31", "08:30", "+03:30")
        self.assertUtc((1356, 8, 10), (12, 0), "1977-11-01", "08:00", "+04:00")
        # 10 Dey 1357 is the first +03:30 civil day after the +04:00 base.
        self.assertUtc((1357, 10, 9), (12, 0), "1978-12-30", "08:00", "+04:00")
        self.assertUtc((1357, 10, 10), (12, 0), "1978-12-31", "08:30", "+03:30")
        self.assertUtc((1358, 4, 15), (12, 0), "1979-07-06", "07:30", "+04:30")
        self.assertUtc((1359, 4, 15), (12, 0), "1980-07-06", "07:30", "+04:30")
        self.assertUtc((1370, 4, 15), (12, 0), "1991-07-06", "08:30", "+03:30")
        self.assertUtc((1371, 4, 15), (12, 0), "1992-07-06", "07:30", "+04:30")
        self.assertUtc((1380, 4, 15), (12, 0), "2001-07-06", "07:30", "+04:30")
        self.assertUtc((1386, 4, 15), (12, 0), "2007-07-06", "08:30", "+03:30")
        self.assertUtc((1390, 4, 15), (14, 30), "2011-07-06", "10:00", "+04:30")
        self.assertUtc((1401, 4, 15), (12, 0), "2022-07-06", "07:30", "+04:30")
        self.assertUtc((1402, 4, 15), (12, 0), "2023-07-06", "08:30", "+03:30")

    def test_transition_edges_are_labeled_and_converted(self):
        gap = self.assertUtc(
            (1356, 8, 10), (0, 15), "1977-11-01", "20:15", "+04:00", status="nonexistent"
        )
        self.assertEqual(gap["utc_datetime"], datetime(1977, 10, 31, 20, 15))
        spring_gap = self.assertUtc(
            (1357, 1, 1), (0, 30), "1978-03-21", "19:30", "+05:00", status="nonexistent"
        )
        self.assertEqual(spring_gap["utc_datetime"].date().isoformat(), "1978-03-20")
        self.assertUtc(
            (1357, 6, 31), (23, 30), "1978-09-22", "18:30", "+05:00", status="ambiguous"
        )
        self.assertUtc(
            (1357, 10, 9), (23, 45), "1978-12-30", "19:45", "+04:00", status="ambiguous"
        )
        self.assertUtc(
            (1401, 1, 1), (0, 30), "2022-03-21", "20:00", "+04:30", status="nonexistent"
        )
        self.assertEqual(
            self.convert((1401, 1, 1), (0, 30))["utc_datetime"],
            datetime(2022, 3, 20, 20, 0),
        )
        self.assertUtc(
            (1401, 6, 31), (23, 30), "2022-09-22", "19:00", "+04:30", status="ambiguous"
        )
        self.assertUtc((1401, 7, 1), (0, 0), "2022-09-23", "20:30", "+03:30")
        self.assertUtc((1402, 6, 31), (23, 30), "2023-09-22", "20:00", "+03:30")

    def test_julian_day_matches_swisseph_for_a_known_utc_instant(self):
        result = self.convert((1390, 4, 15), (14, 30))
        self.assertEqual(result["utc_datetime"], datetime(2011, 7, 6, 10, 0))
        self.assertAlmostEqual(result["julian_day"], swe.julday(2011, 7, 6, 10.0), places=7)


class ZoneinfoDisagreementTests(unittest.TestCase):
    """Image rules win wherever pytz's Asia/Tehran says something else."""

    def test_listed_disagreements_really_differ(self):
        self.assertGreaterEqual(len(TZDATA_DISAGREEMENTS), 10)
        for row in TZDATA_DISAGREEMENTS:
            jalali = row["jalali"]
            ours = offset_of(jalali, (12, 0))["offset"]
            theirs = pytz_offset(jalali)
            self.assertNotEqual(ours, theirs, row["note"])

    def test_boundary_days_pytz_misses(self):
        # Spring starts a day late in pytz, autumn ends a day early.
        for jalali in (
            (1371, 1, 1),
            (1384, 1, 1),
            (1387, 1, 1),
            (1401, 1, 1),
            (1371, 6, 31),
            (1384, 6, 31),
            (1387, 6, 31),
            (1401, 6, 31),
        ):
            ours = offset_of(jalali, (12, 0))
            self.assertEqual(ours["offset_str"], "+04:30", jalali)
            self.assertEqual(pytz_offset(jalali), timedelta(hours=3, minutes=30), jalali)

    def test_quiet_days_where_pytz_agrees(self):
        agreed = (
            ((1356, 8, 10), "+04:00"),
            ((1357, 4, 15), "+05:00"),
            ((1357, 7, 1), "+04:00"),
            ((1357, 9, 15), "+04:00"),
            ((1358, 4, 15), "+04:30"),
            ((1359, 1, 2), "+04:30"),
            ((1359, 6, 31), "+04:30"),
            ((1359, 7, 1), "+03:30"),
            ((1360, 4, 15), "+03:30"),
            ((1365, 4, 15), "+03:30"),
            ((1371, 4, 15), "+04:30"),
            ((1380, 4, 15), "+04:30"),
            ((1385, 4, 15), "+03:30"),
            ((1386, 4, 15), "+03:30"),
            ((1387, 4, 15), "+04:30"),
            ((1390, 4, 15), "+04:30"),
            ((1390, 10, 1), "+03:30"),
            ((1401, 4, 15), "+04:30"),
            ((1401, 7, 1), "+03:30"),
            ((1402, 4, 15), "+03:30"),
            ((1402, 6, 31), "+03:30"),
        )
        for jalali, text in agreed:
            info = offset_of(jalali, (12, 0))
            self.assertEqual(info["offset_str"], text, jalali)
            self.assertEqual(pytz_offset(jalali), info["offset"], jalali)

    def test_gregorian_helpers_follow_the_same_function(self):
        self.assertFalse(should_apply_dst(1977, 7, 6))
        self.assertTrue(should_apply_dst(1978, 7, 6))
        self.assertFalse(should_apply_dst(1978, 12, 6))
        self.assertFalse(should_apply_dst(1986, 7, 6))
        self.assertFalse(should_apply_dst(1991, 7, 6))
        self.assertTrue(should_apply_dst(1992, 7, 6))
        self.assertFalse(should_apply_dst(2007, 7, 6))
        self.assertTrue(should_apply_dst(2011, 7, 6))
        self.assertTrue(should_apply_dst(2022, 9, 22))
        self.assertFalse(should_apply_dst(2022, 9, 23))
        self.assertFalse(should_apply_dst(2023, 7, 6))

        self.assertFalse(is_dst_active_in_year(1977))
        self.assertTrue(is_dst_active_in_year(1978))
        self.assertFalse(is_dst_active_in_year(1986))
        self.assertFalse(is_dst_active_in_year(1991))
        self.assertTrue(is_dst_active_in_year(2022))
        self.assertFalse(is_dst_active_in_year(2023))

        info = get_dst_info(1991)
        self.assertEqual(info["jalali_year"], 1370)
        self.assertFalse(info["dst_active"])
        self.assertEqual(info["utc_offset"], "+03:30")
        direct = iran_offset_for_jalali(1370, 4, 10, 12, 0)
        self.assertEqual(info["reason"], direct["rule"])


if __name__ == "__main__":
    unittest.main()
