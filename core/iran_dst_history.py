# -*- coding: utf-8 -*-
"""
Iran civil offset for natal charts.

This is the only place that decides the UTC offset of an Iranian local
birth time. ``date_utils`` subtracts whatever this module returns; it does
not keep a second copy of the rules.

The rules are the Solar Hijri table supplied for this project (Tehran).
They are not the IANA ``Asia/Tehran`` zone. Where that zone disagrees, this
table wins. See ``TZDATA_DISAGREEMENTS``.

Offset table
------------
+03:30  Before 10 Aban 1356, and the standard offset from 10 Dey 1357 onward.
+04:00  From 10 Aban 1356 through 9 Dey 1357, outside the 1357 daylight window.
+05:00  1 Farvardin 1357 00:00 through 30 Shahrivar 1357 24:00
        (+04:00 base plus one hour of daylight time).
+04:30  First-half daylight time in 1358, 1359, 1371–1384, and 1387–1401.
+03:30  No daylight time in 1360–1370, 1385, 1386, or from 1402 onward.

"First half" means 1 Farvardin 00:00 through 30 Shahrivar 24:00.
At the start, clocks jump from 00:00 to 01:00.
At the end (24:00 on 30 Shahrivar, which is 00:00 on 1 Mehr), clocks jump
back to 23:00 on 30 Shahrivar.

The two half-hour shifts do not name a clock time. Both are applied at
local midnight at the start of the named day:

- 10 Aban 1356 00:00: clocks forward 30 minutes (+03:30 → +04:00).
- 10 Dey 1357 00:00: clocks back 30 minutes (+04:00 → +03:30).

Ambiguous and nonexistent local times
--------------------------------------
Spring-forward gaps (that clock reading never happened):

- 10 Aban 1356, 00:00–00:29
- 1 Farvardin of a daylight-time year, 00:00–00:59

Resolution: the post-transition offset. The written time is converted as
if the clock had already been moved.

Fall-back overlaps (the same reading happens twice):

- 30 Shahrivar of a daylight-time year, 23:00–23:59
- 9 Dey 1357, 23:30–23:59

Resolution: the earlier occurrence, which is the offset still in effect
before the setback. Daylight time therefore stays in force through the
first pass of 23:00–24:00 on 30 Shahrivar.
"""

from datetime import timedelta

import jdatetime

# Standard and historical base offsets.
OFFSET_0330 = timedelta(hours=3, minutes=30)
OFFSET_0400 = timedelta(hours=4)
OFFSET_0430 = timedelta(hours=4, minutes=30)
OFFSET_0500 = timedelta(hours=5)

# Solar Hijri years whose first half observes +1 hour of daylight time
# on top of the standard offset then in force (1357's standard offset is
# +04:00, so that year is +05:00; every later year in this set is +04:30).
def _daylight_year(jalali_year):
    if jalali_year == 1357:
        return True
    if jalali_year in (1358, 1359):
        return True
    if 1371 <= jalali_year <= 1384:
        return True
    if 1387 <= jalali_year <= 1401:
        return True
    return False


def _offset_str(offset):
    total = int(offset.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    hours, minutes = divmod(total // 60, 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


def _result(offset, dst_applied, status, resolution, rule):
    return {
        "offset": offset,
        "offset_str": _offset_str(offset),
        "offset_minutes": int(offset.total_seconds() // 60),
        "dst_applied": dst_applied,
        "local_time_status": status,
        "resolution": resolution,
        "rule": rule,
    }


def iran_offset_for_jalali(year, month, day, hour, minute):
    """
    UTC offset for a Solar Hijri civil time in Iran.

    Args:
        year, month, day: Solar Hijri date
        hour, minute: local clock time, 00:00–23:59

    Returns:
        dict with ``offset`` (timedelta), ``offset_str``, ``dst_applied``,
        ``local_time_status`` (``unique``, ``ambiguous``, or ``nonexistent``),
        ``resolution``, and ``rule``.

    Raises:
        ValueError: if the date or the clock time does not exist on the
        Solar Hijri calendar. A clock time inside a DST gap is not an
        error; it is returned with status ``nonexistent`` and the
        post-transition offset.
    """
    if not isinstance(hour, int) or not isinstance(minute, int):
        raise ValueError("ساعت محلی باید عدد صحیح باشد")
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"ساعت محلی نامعتبر است: {hour:02d}:{minute:02d}")

    # Reject impossible civil dates (30 Esfand in a non-leap year, month 13, …).
    try:
        jdatetime.date(year, month, day)
    except ValueError as exc:
        raise ValueError(f"تاریخ شمسی نامعتبر است: {year}-{month:02d}-{day:02d}") from exc

    stamp = (year, month, day, hour, minute)

    # 10 Aban 1356, 00:00–00:29 did not occur (+03:30 jumped to +04:00).
    if (1356, 8, 10, 0, 0) <= stamp <= (1356, 8, 10, 0, 29):
        return _result(
            OFFSET_0400,
            False,
            "nonexistent",
            "10 Aban 1356 00:00 clocks advanced 30 minutes; "
            "a time inside the gap uses the post-transition offset +04:00",
            "10 Aban 1356: base offset becomes +04:00",
        )

    # 1 Farvardin 1357, 00:00–00:59 did not occur (+04:00 jumped to +05:00).
    if (1357, 1, 1, 0, 0) <= stamp <= (1357, 1, 1, 0, 59):
        return _result(
            OFFSET_0500,
            True,
            "nonexistent",
            "1 Farvardin 1357 00:00 clocks advanced 1 hour; "
            "a time inside the gap uses the post-transition offset +05:00",
            "spring 1357: daylight +1 hour on the +04:00 base (+05:00)",
        )

    # 30 Shahrivar 1357, 23:00–23:59 happened twice. Keep the earlier, +05:00.
    if (1357, 6, 31, 23, 0) <= stamp <= (1357, 6, 31, 23, 59):
        return _result(
            OFFSET_0500,
            True,
            "ambiguous",
            "30 Shahrivar 1357 24:00 clocks went back 1 hour; "
            "the repeated hour uses the earlier occurrence (+05:00)",
            "autumn 1357: daylight ends, offset returns to +04:00",
        )

    # 9 Dey 1357, 23:30–23:59 happened twice. Keep the earlier, +04:00.
    if (1357, 10, 9, 23, 30) <= stamp <= (1357, 10, 9, 23, 59):
        return _result(
            OFFSET_0400,
            False,
            "ambiguous",
            "10 Dey 1357 00:00 clocks went back 30 minutes; "
            "the repeated half-hour uses the earlier occurrence (+04:00)",
            "10 Dey 1357: standard offset returns to +03:30",
        )

    if year != 1357 and _daylight_year(year):
        if (year, 1, 1, 0, 0) <= stamp <= (year, 1, 1, 0, 59):
            return _result(
                OFFSET_0430,
                True,
                "nonexistent",
                f"1 Farvardin {year} 00:00 clocks advanced 1 hour; "
                "a time inside the gap uses the post-transition offset +04:30",
                _daylight_rule(year),
            )
        if (year, 6, 31, 23, 0) <= stamp <= (year, 6, 31, 23, 59):
            return _result(
                OFFSET_0430,
                True,
                "ambiguous",
                f"30 Shahrivar {year} 24:00 clocks went back 1 hour; "
                "the repeated hour uses the earlier occurrence (+04:30)",
                _daylight_rule(year),
            )

    # Before the 10 Aban 1356 advance. The gap minutes were returned above,
    # so everything still below 00:30 that morning is the old offset.
    if stamp < (1356, 8, 10, 0, 30):
        return _result(
            OFFSET_0330,
            False,
            "unique",
            "unique local time",
            "before 10 Aban 1356: standard offset +03:30",
        )

    # +04:00 base, before daylight time starts on 1 Farvardin 1357.
    if stamp < (1357, 1, 1, 0, 0):
        return _result(
            OFFSET_0400,
            False,
            "unique",
            "unique local time",
            "10 Aban 1356: base offset becomes +04:00",
        )

    # 1357 daylight body: 01:00 on 1 Farvardin through 22:59 on 30 Shahrivar.
    if stamp < (1357, 6, 31, 23, 0):
        return _result(
            OFFSET_0500,
            True,
            "unique",
            "unique local time",
            "spring 1357: daylight +1 hour on the +04:00 base (+05:00)",
        )

    # After the 1357 fall-back, until the half-hour overlap on 9 Dey.
    if stamp < (1357, 10, 9, 23, 30):
        return _result(
            OFFSET_0400,
            False,
            "unique",
            "unique local time",
            "autumn 1357: daylight ends, offset returns to +04:00",
        )

    # From 10 Dey 1357 00:00 onward the standard offset is +03:30.
    if _daylight_year(year) and (year, 1, 1, 1, 0) <= stamp < (year, 6, 31, 23, 0):
        return _result(
            OFFSET_0430,
            True,
            "unique",
            "unique local time",
            _daylight_rule(year),
        )

    return _result(
        OFFSET_0330,
        False,
        "unique",
        "unique local time",
        _standard_rule(year),
    )


def _daylight_rule(jalali_year):
    if jalali_year == 1357:
        return "spring 1357: daylight +1 hour on the +04:00 base (+05:00)"
    if jalali_year in (1358, 1359):
        return f"{jalali_year}: first-half daylight time, offset +04:30"
    if 1371 <= jalali_year <= 1384:
        return f"{jalali_year}: first-half daylight time (1371–1384), offset +04:30"
    if 1387 <= jalali_year <= 1401:
        return f"{jalali_year}: first-half daylight time (1387–1401), offset +04:30"
    return f"{jalali_year}: standard offset +03:30"


def _standard_rule(jalali_year):
    if 1360 <= jalali_year <= 1370:
        return f"{jalali_year}: no daylight time (1360–1370), offset +03:30"
    if jalali_year in (1385, 1386):
        return f"{jalali_year}: no daylight time (1385–1386), offset +03:30"
    if jalali_year >= 1402:
        return f"{jalali_year}: no daylight time (from 1402), offset +03:30"
    if jalali_year < 1356:
        return "before 10 Aban 1356: standard offset +03:30"
    return f"{jalali_year}: standard offset +03:30"


def _gregorian_noon_offset(year, month, day):
    """Offset at local noon, which is never inside an Iran transition fold."""
    jalali = jdatetime.date.fromgregorian(year=year, month=month, day=day)
    return iran_offset_for_jalali(jalali.year, jalali.month, jalali.day, 12, 0)


def should_apply_dst(year, month, day):
    """
    Whether seasonal daylight time is in effect at local noon on a Gregorian date.

    Noon is used so the 00:00 gap and the 23:00 overlap are not mistaken for
    the whole civil day. The +04:00 base used from 10 Aban 1356 until 10 Dey
    1357 is a standard-offset change, not daylight time, and returns False.
    """
    return _gregorian_noon_offset(year, month, day)["dst_applied"]


def is_dst_active_in_year(year):
    """
    Whether the Solar Hijri year that contains 1 July of this Gregorian year
    observes first-half daylight time.

    1 July always falls in Tir, inside that year's first half.
    """
    jalali = jdatetime.date.fromgregorian(year=year, month=7, day=1)
    return _daylight_year(jalali.year)


def get_dst_info(year):
    """
    Describe daylight time for the Solar Hijri year that contains 1 July
    of the given Gregorian year. The reason text comes from the same offset
    function used to convert birth times.
    """
    info = _gregorian_noon_offset(year, 7, 1)
    jalali = jdatetime.date.fromgregorian(year=year, month=7, day=1)
    return {
        "year": year,
        "jalali_year": jalali.year,
        "dst_active": info["dst_applied"],
        "utc_offset": info["offset_str"],
        "reason": info["rule"],
    }


# Midday samples where pytz 2024.1's bundled Asia/Tehran (what
# ``pytz.timezone("Asia/Tehran")`` returns in this project) and this table
# disagree. The chart rule wins for every row. The OS zoneinfo file is not
# consulted; on this machine it also differs from pytz on the 1978 return
# to +03:30 (10 November in zoneinfo, 31 December in pytz).
# Checked by tests/test_iran_offset.py.
TZDATA_DISAGREEMENTS = (
    {
        "jalali": (1300, 1, 1),
        "note": "Until 13 June 1935, pytz Asia/Tehran is Local/Tehran Mean Time "
        "+03:26. The chart rule is +03:30 for every local time before 10 Aban 1356.",
    },
    {
        "jalali": (1356, 4, 15),
        "note": "22 March 1977 through 20 October 1977, Asia/Tehran observes "
        "daylight time at +04:30. Solar Hijri 1356 has no daylight time; "
        "summer 1356 stays +03:30.",
    },
    {
        "jalali": (1356, 8, 9),
        "note": "After the 20 October 1977 fall-back, Asia/Tehran is already "
        "+04:00. The chart rule stays +03:30 until 10 Aban 1356 (1 November 1977). "
        "Noon on 10 Aban itself agrees: both are +04:00.",
    },
    {
        "jalali": (1357, 1, 3),
        "note": "Asia/Tehran starts +05:00 on 25 March 1978 (5 Farvardin 1357). "
        "The chart rule starts at 1 Farvardin 1357 00:00 (21 March 1978). "
        "Midsummer 1357 (15 Tir) agrees at +05:00.",
    },
    {
        "jalali": (1357, 5, 20),
        "note": "Asia/Tehran ends +05:00 on 5 August 1978 (14 Mordad 1357). "
        "The chart rule keeps +05:00 until 30 Shahrivar 1357 24:00 "
        "(22 September 1978). 1 Mehr 1357 agrees again at +04:00.",
    },
    {
        "jalali": (1357, 10, 10),
        "note": "pytz moves +04:00 back to +03:30 at 24:00 on 31 December 1978, "
        "so noon on 10 Dey 1357 is still +04:00 there. The chart rule treats "
        "10 Dey as the first civil day of +03:30 (clocks back 30 minutes at "
        "00:00). Azar 1357 agrees: both are still +04:00.",
    },
    {
        "jalali": (1358, 2, 10),
        "note": "Asia/Tehran starts 1358 daylight time on 27 May 1979 "
        "(6 Khordad 1358), not on 1 Farvardin 1358. "
        "15 Tir 1358 agrees: both are +04:30.",
    },
    {
        "jalali": (1358, 6, 28),
        "note": "Asia/Tehran ends 1358 daylight time on 18 September 1979 "
        "(27 Shahrivar). 28 Shahrivar 1358 is still +04:30 on the chart rule "
        "and already +03:30 in Asia/Tehran. 1359 agrees on both edges "
        "(21 March 1980 and 22 September 1980).",
    },
    {
        "jalali": (1370, 4, 15),
        "note": "Asia/Tehran observes daylight time from 3 May 1991 "
        "(13 Ordibehesht 1370) through 21 September 1991. "
        "1360–1370 have no daylight time on the chart rule. "
        "1365 summer agrees: both are +03:30.",
    },
    {
        "jalali": (1371, 1, 1),
        "note": "From 1992 through 2022, Asia/Tehran's spring transition is a "
        "fixed Gregorian midnight (usually 22 March 01:00), not 1 Farvardin "
        "00:00. Noon on 1 Farvardin 1371 (21 March 1992), 1384 (21 March 2005), "
        "1387 (20 March 2008), and 1401 (21 March 2022) is +04:30 on the chart "
        "rule and +03:30 in Asia/Tehran. The next day agrees.",
    },
    {
        "jalali": (1371, 6, 31),
        "note": "Asia/Tehran ends daylight time at the close of 21 September, "
        "which is 29 Shahrivar in these years, not 30 Shahrivar 24:00. "
        "Noon on 30 Shahrivar 1371, 1384, 1387, and 1401 is +04:30 on the "
        "chart rule and +03:30 in Asia/Tehran. 29 Shahrivar and 1 Mehr agree. "
        "Midsummer 1380, 1390, and 1401 agree at +04:30. "
        "1385, 1386, and 1402 agree at +03:30 with no daylight time.",
    },
)
