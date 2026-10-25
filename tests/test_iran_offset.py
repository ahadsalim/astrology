# -*- coding: utf-8 -*-
"""Iran birth-time offset against the primary-source table and IANA tz main."""

import subprocess
import tempfile
import unittest
import zoneinfo
from datetime import datetime
from pathlib import Path

import jdatetime
import swisseph as swe

import utils  # noqa: F401  — same import order as app.py
from core.date_utils import DateTimeConverter
from core.iran_dst_history import (
    MODERN_DST_YEARS,
    PYTZ_2024_1_OUTDATED,
    TZDATA_DISAGREEMENTS,
    get_dst_info,
    iran_offset_for_jalali,
    is_dst_active_in_year,
    should_apply_dst,
)

TEHRAN = None


def setUpModule():
    global TEHRAN
    out = tempfile.mkdtemp(prefix="tehran-tz-")
    src = Path(__file__).resolve().parent / "data" / "asia-tehran"
    subprocess.check_call(["zic", "-d", out, str(src)])
    zoneinfo.reset_tzpath([out])
    TEHRAN = zoneinfo.ZoneInfo("Asia/Tehran")


def offset_of(jalali, hm):
    year, month, day = jalali
    hour, minute = hm
    return iran_offset_for_jalali(year, month, day, hour, minute)


def tz_offset(jalali, hm=(12, 0)):
    year, month, day = jalali
    hour, minute = hm
    gregorian = jdatetime.date(year, month, day).togregorian()
    civil = datetime(gregorian.year, gregorian.month, gregorian.day, hour, minute, tzinfo=TEHRAN)
    return civil.utcoffset()


def allowed_tz_disagreement(stamp):
    """Windows where the owner or an uncertain source differs from tz main."""
    if stamp < (1314, 3, 22, 0, 0):
        return True
    if (1356, 1, 1, 0, 0) <= stamp <= (1356, 1, 1, 23, 59):
        return True
    if (1357, 1, 4, 0, 0) <= stamp <= (1357, 1, 5, 0, 59):
        return True
    if (1358, 6, 28, 0, 0) <= stamp <= (1358, 6, 30, 23, 59):
        return True
    year = stamp[0]
    if year in MODERN_DST_YEARS and (year, 1, 1, 0, 0) <= stamp <= (year, 1, 2, 0, 59):
        return True
    # Same transition instant as tz main. The missing hour is 00:00–00:59.
    # This table uses the post-transition offset; zoneinfo labels that
    # nonexistent stamp with the offset from before the jump.
    if stamp[3] == 0 and stamp[4] <= 59 and stamp[:3] in (
        (1358, 3, 5), (1359, 1, 1), (1370, 2, 13),
    ):
        return True
    return False


class IranOffsetTableTests(unittest.TestCase):
    def assertOffset(self, jalali, hm, expected, status="unique", dst=None):
        info = offset_of(jalali, hm)
        self.assertEqual(info["offset_str"], expected, info["rule"])
        self.assertEqual(info["local_time_status"], status, info["resolution"])
        if dst is not None:
            self.assertEqual(info["dst_applied"], dst)
        return info

    def test_standard_offset_before_and_after_1314(self):
        self.assertOffset((1300, 1, 1), (12, 0), "+03:30", dst=False)
        self.assertOffset((1314, 3, 21), (23, 59), "+03:30", dst=False)
        self.assertOffset((1314, 3, 22), (0, 0), "+03:30", dst=False)
        self.assertOffset((1355, 12, 15), (23, 59), "+03:30", dst=False)

    def test_1356_starts_at_midnight_entering_farvardin_and_ends_28_mehr(self):
        gap = self.assertOffset((1356, 1, 1), (0, 30), "+04:30", status="nonexistent", dst=True)
        self.assertIn("post-transition", gap["resolution"])
        self.assertIn("Owner decision", gap["rule"])
        self.assertOffset((1356, 1, 1), (1, 0), "+04:30", dst=True)
        self.assertOffset((1356, 1, 1), (23, 59), "+04:30", dst=True)
        self.assertOffset((1356, 4, 15), (12, 0), "+04:30", dst=True)
        self.assertOffset((1356, 7, 28), (23, 29), "+04:30", dst=True)
        overlap = self.assertOffset((1356, 7, 28), (23, 45), "+04:30", status="ambiguous", dst=True)
        self.assertIn("earlier", overlap["resolution"])
        self.assertOffset((1356, 7, 29), (0, 0), "+04:00", dst=False)
        # 10 Aban is not a transition.
        self.assertOffset((1356, 8, 9), (12, 0), "+04:00", dst=False)
        self.assertOffset((1356, 8, 10), (0, 15), "+04:00", dst=False)
        self.assertOffset((1356, 8, 10), (12, 0), "+04:00", dst=False)
        self.assertOffset((1356, 12, 15), (12, 0), "+04:00", dst=False)

    def test_1357_friday_start_mordad_and_aban(self):
        self.assertOffset((1357, 1, 3), (23, 59), "+04:00", dst=False)
        gap = self.assertOffset((1357, 1, 4), (0, 30), "+05:00", status="nonexistent", dst=True)
        self.assertIn("post-transition", gap["resolution"])
        self.assertIn("Uncertain", gap["rule"])
        self.assertOffset((1357, 1, 4), (1, 0), "+05:00", dst=True)
        self.assertOffset((1357, 4, 15), (12, 0), "+05:00", dst=True)
        self.assertOffset((1357, 5, 13), (23, 59), "+05:00", dst=True)
        overlap = self.assertOffset((1357, 5, 14), (0, 30), "+05:00", status="ambiguous", dst=True)
        self.assertIn("earlier", overlap["resolution"])
        self.assertOffset((1357, 5, 14), (1, 0), "+04:00", dst=False)
        self.assertOffset((1357, 8, 19), (23, 29), "+04:00", dst=False)
        self.assertOffset((1357, 8, 19), (23, 45), "+04:00", status="ambiguous", dst=False)
        self.assertOffset((1357, 8, 20), (0, 0), "+03:30", dst=False)
        # 10 Dey is not a transition.
        self.assertOffset((1357, 10, 9), (23, 45), "+03:30", dst=False)
        self.assertOffset((1357, 10, 10), (0, 0), "+03:30", dst=False)
        self.assertOffset((1357, 10, 10), (12, 0), "+03:30", dst=False)

    def test_1358_khordad_to_30_shahrivar(self):
        self.assertOffset((1358, 3, 4), (23, 59), "+03:30", dst=False)
        self.assertOffset((1358, 3, 5), (0, 30), "+04:30", status="nonexistent", dst=True)
        self.assertOffset((1358, 3, 5), (1, 0), "+04:30", dst=True)
        self.assertOffset((1358, 4, 15), (12, 0), "+04:30", dst=True)
        self.assertOffset((1358, 6, 27), (12, 0), "+04:30", dst=True)
        self.assertOffset((1358, 6, 30), (22, 59), "+04:30", dst=True)
        overlap = self.assertOffset((1358, 6, 30), (23, 30), "+04:30", status="ambiguous", dst=True)
        self.assertIn("earlier", overlap["resolution"])
        self.assertIn("27 Shahrivar", overlap["rule"])
        self.assertOffset((1358, 6, 31), (0, 0), "+03:30", dst=False)
        self.assertOffset((1358, 6, 31), (12, 0), "+03:30", dst=False)

    def test_1359_runs_through_31_shahrivar(self):
        self.assertOffset((1359, 1, 1), (0, 30), "+04:30", status="nonexistent", dst=True)
        self.assertOffset((1359, 1, 1), (12, 0), "+04:30", dst=True)
        self.assertOffset((1359, 4, 15), (12, 0), "+04:30", dst=True)
        self.assertOffset((1359, 6, 30), (12, 0), "+04:30", dst=True)
        self.assertOffset((1359, 6, 31), (22, 59), "+04:30", dst=True)
        self.assertOffset((1359, 6, 31), (23, 30), "+04:30", status="ambiguous", dst=True)
        self.assertOffset((1359, 7, 1), (0, 0), "+03:30", dst=False)

    def test_1360_through_1369_have_no_daylight_time(self):
        self.assertOffset((1360, 1, 1), (0, 30), "+03:30", dst=False)
        self.assertOffset((1365, 4, 15), (12, 0), "+03:30", dst=False)
        self.assertOffset((1369, 4, 15), (12, 0), "+03:30", dst=False)
        self.assertOffset((1369, 6, 31), (23, 30), "+03:30", dst=False)

    def test_1370_from_13_ordibehesht_to_30_shahrivar(self):
        self.assertOffset((1370, 2, 12), (23, 59), "+03:30", dst=False)
        gap = self.assertOffset((1370, 2, 13), (0, 30), "+04:30", status="nonexistent", dst=True)
        self.assertIn("uncertain", gap["rule"])
        self.assertOffset((1370, 4, 15), (12, 0), "+04:30", dst=True)
        self.assertOffset((1370, 6, 30), (23, 30), "+04:30", status="ambiguous", dst=True)
        self.assertOffset((1370, 6, 31), (12, 0), "+03:30", dst=False)

    def test_modern_years_start_on_1_farvardin_and_end_on_30_shahrivar(self):
        for year in (1371, 1380, 1384, 1387, 1390, 1401):
            gap = self.assertOffset((year, 1, 1), (0, 30), "+04:30", status="nonexistent", dst=True)
            self.assertIn("Owner decision", gap["rule"])
            self.assertOffset((year, 1, 1), (12, 0), "+04:30", dst=True)
            # 2 Farvardin is already daylight time; it is not the gap.
            self.assertOffset((year, 1, 2), (0, 30), "+04:30", dst=True)
            self.assertOffset((year, 4, 15), (12, 0), "+04:30", dst=True)
            self.assertOffset((year, 6, 30), (22, 59), "+04:30", dst=True)
            self.assertOffset((year, 6, 30), (23, 30), "+04:30", status="ambiguous", dst=True)
            self.assertOffset((year, 6, 31), (0, 0), "+03:30", dst=False)
            self.assertOffset((year, 6, 31), (12, 0), "+03:30", dst=False)
            self.assertOffset((year, 7, 1), (12, 0), "+03:30", dst=False)

    def test_1385_1386_and_1402_onward_have_no_daylight_time(self):
        for year in (1385, 1386, 1402, 1404):
            self.assertOffset((year, 1, 1), (0, 30), "+03:30", dst=False)
            self.assertOffset((year, 4, 15), (12, 0), "+03:30", dst=False)
            self.assertOffset((year, 6, 30), (23, 30), "+03:30", dst=False)
            self.assertOffset((year, 6, 31), (12, 0), "+03:30", dst=False)

    def test_invalid_clock_or_date_is_rejected(self):
        with self.assertRaises(ValueError):
            iran_offset_for_jalali(1390, 4, 15, 24, 0)
        with self.assertRaises(ValueError):
            iran_offset_for_jalali(1390, 12, 31, 12, 0)


class BirthTimeConversionTests(unittest.TestCase):
    def convert(self, jalali, hm):
        year, month, day = jalali
        hour, minute = hm
        return DateTimeConverter.parse_and_convert(
            f"{year:04d}-{month:02d}-{day:02d}",
            f"{hour:02d}:{minute:02d}",
        )

    def assertUtc(self, jalali, hm, gregorian, utc, offset, status="unique"):
        result = self.convert(jalali, hm)
        self.assertEqual(result["gregorian_str"], gregorian)
        self.assertEqual(result["utc_time"], utc)
        self.assertEqual(result["utc_offset"], offset)
        self.assertEqual(result["local_time_status"], status)
        utc_dt = result["utc_datetime"]
        hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        self.assertAlmostEqual(
            result["julian_day"],
            swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal),
            places=7,
        )
        return result

    def test_period_samples_reach_utc(self):
        self.assertUtc((1356, 4, 15), (12, 0), "1977-07-06", "07:30", "+04:30")
        self.assertUtc((1356, 8, 10), (12, 0), "1977-11-01", "08:00", "+04:00")
        self.assertUtc((1357, 4, 15), (12, 0), "1978-07-06", "07:00", "+05:00")
        self.assertUtc((1357, 10, 10), (12, 0), "1978-12-31", "08:30", "+03:30")
        self.assertUtc((1358, 4, 15), (12, 0), "1979-07-06", "07:30", "+04:30")
        self.assertUtc((1358, 6, 31), (12, 0), "1979-09-22", "08:30", "+03:30")
        self.assertUtc((1359, 4, 15), (12, 0), "1980-07-06", "07:30", "+04:30")
        self.assertUtc((1365, 4, 15), (12, 0), "1986-07-06", "08:30", "+03:30")
        self.assertUtc((1370, 4, 15), (12, 0), "1991-07-06", "07:30", "+04:30")
        self.assertUtc((1371, 6, 31), (12, 0), "1992-09-22", "08:30", "+03:30")
        self.assertUtc((1380, 4, 15), (12, 0), "2001-07-06", "07:30", "+04:30")
        self.assertUtc((1386, 4, 15), (12, 0), "2007-07-06", "08:30", "+03:30")
        self.assertUtc((1390, 4, 15), (14, 30), "2011-07-06", "10:00", "+04:30")
        self.assertUtc((1401, 1, 1), (12, 0), "2022-03-21", "07:30", "+04:30")
        self.assertUtc((1401, 6, 31), (12, 0), "2022-09-22", "08:30", "+03:30")
        self.assertUtc((1402, 4, 15), (12, 0), "2023-07-06", "08:30", "+03:30")

    def test_transition_edges_cross_midnight_in_utc(self):
        gap = self.assertUtc(
            (1356, 1, 1), (0, 30), "1977-03-21", "20:00", "+04:30", status="nonexistent"
        )
        self.assertEqual(gap["utc_datetime"], datetime(1977, 3, 20, 20, 0))
        self.assertUtc(
            (1357, 1, 4), (0, 30), "1978-03-24", "19:30", "+05:00", status="nonexistent"
        )
        self.assertUtc(
            (1357, 5, 14), (0, 30), "1978-08-05", "19:30", "+05:00", status="ambiguous"
        )
        self.assertUtc(
            (1357, 8, 19), (23, 45), "1978-11-10", "19:45", "+04:00", status="ambiguous"
        )
        self.assertUtc((1357, 8, 20), (0, 0), "1978-11-11", "20:30", "+03:30")
        self.assertUtc(
            (1401, 1, 1), (0, 30), "2022-03-21", "20:00", "+04:30", status="nonexistent"
        )
        self.assertUtc(
            (1401, 6, 30), (23, 30), "2022-09-21", "19:00", "+04:30", status="ambiguous"
        )
        self.assertUtc((1401, 7, 1), (0, 0), "2022-09-23", "20:30", "+03:30")

    def test_julian_day_matches_swisseph(self):
        result = self.convert((1390, 4, 15), (14, 30))
        self.assertEqual(result["utc_datetime"], datetime(2011, 7, 6, 10, 0))
        self.assertAlmostEqual(result["julian_day"], swe.julday(2011, 7, 6, 10.0), places=7)


class ZoneinfoComparisonTests(unittest.TestCase):
    def test_listed_disagreements_differ_at_noon(self):
        self.assertGreaterEqual(len(TZDATA_DISAGREEMENTS), 5)
        for row in TZDATA_DISAGREEMENTS:
            info = offset_of(row["jalali"], (12, 0))
            self.assertEqual(info["offset_str"], row["offset"], row["note"])
            self.assertNotEqual(info["offset"], tz_offset(row["jalali"]), row["note"])

    def test_pytz_2024_1_stale_dates_match_tz_main(self):
        for row in PYTZ_2024_1_OUTDATED:
            info = offset_of(row["jalali"], (12, 0))
            self.assertNotEqual(info["offset_str"], row["pytz_offset"], row["note"])
            self.assertEqual(info["offset"], tz_offset(row["jalali"]), row["note"])
            self.assertFalse(allowed_tz_disagreement(row["jalali"] + (12, 0)))

    def test_grid_matches_tz_main_outside_documented_windows(self):
        years = (
            1300, 1314, 1350,
            *range(1356, 1363),
            1368, 1369, 1370, 1371, 1372,
            1383, 1384, 1385, 1386, 1387, 1388,
            1390, 1400, 1401, 1402, 1403,
        )
        days = (
            (1, 1), (1, 2), (1, 4), (1, 5),
            (2, 12), (2, 13), (3, 4), (3, 5),
            (4, 15), (5, 14),
            (6, 27), (6, 28), (6, 30), (6, 31), (7, 1),
            (7, 28), (7, 29), (8, 10), (8, 19), (8, 20), (10, 10),
        )
        clocks = ((0, 30), (12, 0), (23, 30))
        unexpected = []
        for year in years:
            for month, day in days:
                for hm in clocks:
                    stamp = (year, month, day, hm[0], hm[1])
                    ours = offset_of((year, month, day), hm)["offset"]
                    theirs = tz_offset((year, month, day), hm)
                    if ours != theirs and not allowed_tz_disagreement(stamp):
                        unexpected.append((stamp, ours, theirs))
        self.assertEqual(unexpected, [])

    def test_shared_gap_hour_is_a_label_not_a_different_instant(self):
        shared = (
            ((1358, 3, 5), "+04:30", "+03:30"),
            ((1359, 1, 1), "+04:30", "+03:30"),
            ((1370, 2, 13), "+04:30", "+03:30"),
        )
        for jalali, after, before in shared:
            info = offset_of(jalali, (0, 30))
            self.assertEqual(info["local_time_status"], "nonexistent", jalali)
            self.assertEqual(info["offset_str"], after, jalali)
            before_td = tz_offset(jalali, (0, 30))
            self.assertEqual(
                f"+{int(before_td.total_seconds() // 3600):02d}:{int((before_td.total_seconds() % 3600) // 60):02d}",
                before,
                jalali,
            )
            self.assertEqual(offset_of(jalali, (1, 0))["offset"], tz_offset(jalali, (1, 0)), jalali)

    def test_quiet_edges_match_tz_main(self):
        agreed = (
            ((1356, 1, 2), (12, 0), "+04:30"),
            ((1356, 7, 29), (12, 0), "+04:00"),
            ((1356, 8, 10), (12, 0), "+04:00"),
            ((1357, 1, 5), (12, 0), "+05:00"),
            ((1357, 5, 14), (12, 0), "+04:00"),
            ((1357, 8, 20), (12, 0), "+03:30"),
            ((1357, 10, 10), (12, 0), "+03:30"),
            ((1358, 3, 5), (12, 0), "+04:30"),
            ((1358, 6, 27), (12, 0), "+04:30"),
            ((1358, 6, 31), (12, 0), "+03:30"),
            ((1359, 1, 1), (12, 0), "+04:30"),
            ((1359, 6, 31), (12, 0), "+04:30"),
            ((1359, 7, 1), (12, 0), "+03:30"),
            ((1365, 4, 15), (12, 0), "+03:30"),
            ((1370, 2, 13), (12, 0), "+04:30"),
            ((1370, 6, 31), (12, 0), "+03:30"),
            ((1371, 1, 2), (12, 0), "+04:30"),
            ((1371, 6, 30), (12, 0), "+04:30"),
            ((1371, 6, 31), (12, 0), "+03:30"),
            ((1384, 6, 31), (12, 0), "+03:30"),
            ((1386, 4, 15), (12, 0), "+03:30"),
            ((1387, 1, 2), (12, 0), "+04:30"),
            ((1401, 1, 2), (12, 0), "+04:30"),
            ((1401, 6, 31), (12, 0), "+03:30"),
            ((1402, 4, 15), (12, 0), "+03:30"),
            ((1402, 6, 31), (12, 0), "+03:30"),
        )
        for jalali, hm, text in agreed:
            info = offset_of(jalali, hm)
            self.assertEqual(info["offset_str"], text, jalali)
            self.assertEqual(tz_offset(jalali, hm), info["offset"], jalali)

    def test_gregorian_helpers_follow_the_same_function(self):
        self.assertTrue(should_apply_dst(1977, 7, 6))
        self.assertFalse(should_apply_dst(1977, 11, 1))
        self.assertTrue(should_apply_dst(1978, 3, 24))
        self.assertFalse(should_apply_dst(1978, 8, 5))
        self.assertFalse(should_apply_dst(1986, 7, 6))
        self.assertTrue(should_apply_dst(1991, 7, 6))
        self.assertTrue(should_apply_dst(1992, 3, 21))
        self.assertFalse(should_apply_dst(1992, 9, 22))
        self.assertFalse(should_apply_dst(2007, 7, 6))
        self.assertTrue(should_apply_dst(2022, 3, 21))
        self.assertTrue(should_apply_dst(2022, 9, 21))
        self.assertFalse(should_apply_dst(2022, 9, 22))
        self.assertFalse(should_apply_dst(2023, 7, 6))

        self.assertTrue(is_dst_active_in_year(1977))
        self.assertFalse(is_dst_active_in_year(1986))
        self.assertTrue(is_dst_active_in_year(1991))
        self.assertFalse(is_dst_active_in_year(2007))
        self.assertTrue(is_dst_active_in_year(2022))
        self.assertFalse(is_dst_active_in_year(2023))

        info = get_dst_info(1991)
        self.assertEqual(info["jalali_year"], 1370)
        self.assertTrue(info["dst_active"])
        self.assertEqual(info["utc_offset"], "+04:30")
        direct = iran_offset_for_jalali(1370, 4, 10, 12, 0)
        self.assertEqual(info["reason"], direct["rule"])


if __name__ == "__main__":
    unittest.main()
