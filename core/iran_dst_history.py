# -*- coding: utf-8 -*-
"""
Iran civil offset for natal charts.

``iran_offset_for_jalali`` is the only place that decides the UTC offset of
an Iranian local birth time. ``date_utils`` subtracts whatever it returns.

The table follows contemporary reports and cabinet decrees (Ettela'at,
Kayhan, Aftab-e Sharq), which current IANA tz main also follows, except
where this file documents an owner decision or an uncertain reading.
It does not follow the earlier image table, and it does not call pytz.

Offset table (Solar Hijri, Tehran clock)
-----------------------------------------
+03:30  Standard offset. Also used before 22 Khordad 1314. tz main uses
        local/Tehran mean time +03:25:44 until that morning; that is
        documented and not applied.
+04:30  Daylight time: 1 Farvardin 1356 00:00 through 28 Mehr 1356 24:00;
        5 Khordad 1358 00:00 through 30 Shahrivar 1358 24:00;
        1 Farvardin 1359 00:00 through 31 Shahrivar 1359 24:00;
        13 Ordibehesht 1370 00:00 through 30 Shahrivar 1370 24:00;
        1 Farvardin 00:00 through 30 Shahrivar 24:00 in 1371–1384 and
        1387–1401.
+04:00  From 29 Mehr 1356 through 3 Farvardin 1357, and from 14 Mordad
        1357 01:00 through 19 Aban 1357 24:00. A standard-offset change,
        not an extra hour of daylight time.
+05:00  4 Farvardin 1357 00:00 through 14 Mordad 1357 01:00
        (+04:00 base plus one hour).
+03:30  No daylight time in 1360–1369, 1385, 1386, or from 1402 on.

Where the clock moves
----------------------
Forward one hour, so the named hour never happens. A time inside the gap
uses the post-transition offset.

- 1356, 1359, 1371–1384, 1387–1401: 00:00 at the start of 1 Farvardin
  (the night entering 1 Farvardin). Gap = 1 Farvardin 00:00–00:59.
  Owner decision. The cabinet decree says the clocks move at "24:00 of
  1 Farvardin", and current tz main reads that as the end of 1 Farvardin
  (gap on 2 Farvardin) for 1371–1401. 1356 in tz main is instead 23:00 on
  1 Farvardin. 1359 in tz main (20 March 1980 24:00) is the same instant
  as this 00:00 start.
- 1357: 00:00 at the start of 4 Farvardin, the first Friday of Farvardin.
  Gap = 4 Farvardin 00:00–00:59. Kayhan describes 24:00 at the end of that
  day (tz main's reading, gap on 5 Farvardin). That reading is uncertain.
- 1358: 00:00 at the start of 5 Khordad (24:00 at the end of 4 Khordad).
  Gap = 5 Khordad 00:00–00:59.
- 1370: 00:00 at the start of 13 Ordibehesht. Gap = 13 Ordibehesht
  00:00–00:59. This matches tz main and timeanddate; the contemporary
  notice for the start is thin, so the instant is uncertain.

Back, so the named minutes happen twice. The earlier occurrence is used.

- 28 Mehr 1356 24:00: +04:30 to +04:00. 23:30–23:59 repeats.
- 14 Mordad 1357 01:00: +05:00 to +04:00. 00:00–00:59 repeats.
- 19 Aban 1357 24:00: +04:00 to +03:30. 23:30–23:59 repeats.
- 30 Shahrivar 24:00 in 1358, 1370, 1371–1384 and 1387–1401: +04:30 to
  +03:30. 23:00–23:59 repeats. Shahrivar has 31 days, so 31 Shahrivar is
  already standard time. For 1358, tz main ends instead at 24:00 on
  27 Shahrivar; that alternative is uncertain. The cabinet decree used
  here names 30 Shahrivar.
- 31 Shahrivar 1359 24:00: +04:30 to +03:30. 23:00–23:59 repeats.

There is no 10 Aban 1356 shift and no 10 Dey 1357 shift.
"""

from datetime import timedelta

import jdatetime

OFFSET_0330 = timedelta(hours=3, minutes=30)
OFFSET_0400 = timedelta(hours=4)
OFFSET_0430 = timedelta(hours=4, minutes=30)
OFFSET_0500 = timedelta(hours=5)

# Daylight time that begins on 1 Farvardin and ends at 24:00 on 30 Shahrivar.
MODERN_DST_YEARS = tuple(range(1371, 1385)) + tuple(range(1387, 1402))

_OWNER_FARVARDIN = (
    "Owner decision: the forward change is at 00:00 at the start of "
    "1 Farvardin (the night entering 1 Farvardin), so 00:00–00:59 is the gap. "
    "The decree text says 24:00 of 1 Farvardin, which tz main reads as the "
    "end of that day (gap on 2 Farvardin) for 1371–1401."
)


def _offset_str(offset):
    total = int(offset.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    hours, minutes = divmod(total // 60, 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


def _pack(offset, status, resolution, rule):
    return {
        "offset": offset,
        "offset_str": _offset_str(offset),
        "offset_minutes": int(offset.total_seconds() // 60),
        "dst_applied": offset in (OFFSET_0430, OFFSET_0500),
        "local_time_status": status,
        "resolution": resolution,
        "rule": rule,
    }


def _gap(year, month, day, before, after, rule, after_rule):
    return {
        "start": (year, month, day, 0, 0),
        "end": (year, month, day, 0, 59),
        "kind": "gap",
        "before": before,
        "after": after,
        "rule": rule,
        "after_rule": after_rule,
        "resolution": (
            f"{year:04d}-{month:02d}-{day:02d} 00:00 clocks advanced 1 hour; "
            f"a time inside the gap uses the post-transition offset {_offset_str(after)}"
        ),
    }


def _overlap(year, month, day, hour, minute, before, after, rule, after_rule, when):
    return {
        "start": (year, month, day, hour, minute),
        "end": (year, month, day, hour, 59),
        "kind": "overlap",
        "before": before,
        "after": after,
        "rule": rule,
        "after_rule": after_rule,
        "resolution": (
            f"{when}; the repeated clock time uses the earlier occurrence "
            f"({_offset_str(before)})"
        ),
    }


def _build_transitions():
    rows = []

    rows.append(_gap(
        1356, 1, 1, OFFSET_0330, OFFSET_0430,
        "1356: +03:30 to +04:30 at 00:00 on 1 Farvardin. " + _OWNER_FARVARDIN
        + " tz main instead moves the clock at 23:00 on 1 Farvardin.",
        "1356 daylight time +04:30 until 24:00 on 28 Mehr",
    ))
    rows.append(_overlap(
        1356, 7, 28, 23, 30, OFFSET_0430, OFFSET_0400,
        "28 Mehr 1356 24:00: +04:30 back to +04:00",
        "+04:00 from 29 Mehr 1356 until 00:00 on 4 Farvardin 1357",
        "28 Mehr 1356 24:00 clocks went back 30 minutes",
    ))

    rows.append(_gap(
        1357, 1, 4, OFFSET_0400, OFFSET_0500,
        "1357: +04:00 to +05:00 at 00:00 on 4 Farvardin, the first Friday "
        "of Farvardin. Uncertain: Kayhan and tz main put the same change at "
        "24:00 at the end of 4 Farvardin (gap on 5 Farvardin).",
        "1357 daylight time +05:00 until 01:00 on 14 Mordad",
    ))
    rows.append(_overlap(
        1357, 5, 14, 0, 0, OFFSET_0500, OFFSET_0400,
        "14 Mordad 1357 01:00: +05:00 back to +04:00",
        "+04:00 from 14 Mordad 1357 01:00 until 24:00 on 19 Aban",
        "14 Mordad 1357 01:00 clocks went back 1 hour",
    ))
    rows.append(_overlap(
        1357, 8, 19, 23, 30, OFFSET_0400, OFFSET_0330,
        "19 Aban 1357 24:00: +04:00 back to +03:30",
        "standard offset +03:30 from 20 Aban 1357",
        "19 Aban 1357 24:00 clocks went back 30 minutes",
    ))

    rows.append(_gap(
        1358, 3, 5, OFFSET_0330, OFFSET_0430,
        "1358: +03:30 to +04:30 at 00:00 on 5 Khordad (24:00 at the end of 4 Khordad)",
        "1358 daylight time +04:30 until 24:00 on 30 Shahrivar. "
        "Uncertain alternative in tz main: 24:00 on 27 Shahrivar.",
    ))
    rows.append(_overlap(
        1358, 6, 30, 23, 0, OFFSET_0430, OFFSET_0330,
        "30 Shahrivar 1358 24:00: daylight time ends. "
        "Uncertain alternative in tz main: 24:00 on 27 Shahrivar.",
        "standard offset +03:30 after 30 Shahrivar 1358",
        "30 Shahrivar 1358 24:00 clocks went back 1 hour",
    ))

    rows.append(_gap(
        1359, 1, 1, OFFSET_0330, OFFSET_0430,
        "1359: +03:30 to +04:30 at 00:00 on 1 Farvardin. " + _OWNER_FARVARDIN
        + " For 1359 this is the same instant tz main uses.",
        "1359 daylight time +04:30 until 24:00 on 31 Shahrivar",
    ))
    rows.append(_overlap(
        1359, 6, 31, 23, 0, OFFSET_0430, OFFSET_0330,
        "31 Shahrivar 1359 24:00: daylight time ends",
        "1360–1369: no daylight time, standard offset +03:30",
        "31 Shahrivar 1359 24:00 clocks went back 1 hour",
    ))

    rows.append(_gap(
        1370, 2, 13, OFFSET_0330, OFFSET_0430,
        "1370: +03:30 to +04:30 at 00:00 on 13 Ordibehesht. "
        "Matches tz main and timeanddate; the contemporary notice for this "
        "start is thin, so the instant is uncertain.",
        "1370 daylight time +04:30 until 24:00 on 30 Shahrivar",
    ))
    rows.append(_overlap(
        1370, 6, 30, 23, 0, OFFSET_0430, OFFSET_0330,
        "30 Shahrivar 1370 24:00: daylight time ends",
        "standard offset +03:30 after 30 Shahrivar 1370",
        "30 Shahrivar 1370 24:00 clocks went back 1 hour",
    ))

    for year in MODERN_DST_YEARS:
        rows.append(_gap(
            year, 1, 1, OFFSET_0330, OFFSET_0430,
            f"{year}: +03:30 to +04:30 at 00:00 on 1 Farvardin. " + _OWNER_FARVARDIN,
            f"{year}: first-half daylight time +04:30 until 24:00 on 30 Shahrivar",
        ))
        rows.append(_overlap(
            year, 6, 30, 23, 0, OFFSET_0430, OFFSET_0330,
            f"30 Shahrivar {year} 24:00: daylight time ends. "
            "Shahrivar has 31 days; 31 Shahrivar is standard time.",
            f"standard offset +03:30 after 30 Shahrivar {year}",
            f"30 Shahrivar {year} 24:00 clocks went back 1 hour",
        ))

    for earlier, later in zip(rows, rows[1:]):
        if earlier["start"] >= later["start"] or earlier["end"] >= later["start"]:
            raise RuntimeError(f"Iran offset transitions overlap: {earlier['start']} / {later['start']}")
    return tuple(rows)


TRANSITIONS = _build_transitions()


def _baseline_rule(stamp):
    if stamp < (1314, 3, 22, 0, 0):
        return (
            "standard offset +03:30. tz main uses local mean time +03:25:44 "
            "before 22 Khordad 1314 (13 June 1935); that difference is not applied"
        )
    return "standard offset +03:30"


def iran_offset_for_jalali(year, month, day, hour, minute):
    """
    UTC offset for one Solar Hijri civil time in Iran.

    Returns offset, offset_str, dst_applied, local_time_status
    (``unique``, ``ambiguous``, or ``nonexistent``), resolution, and rule.

    A gap is not an error: it is returned as ``nonexistent`` with the
    post-transition offset. A repeated hour is returned as ``ambiguous``
    with the earlier offset.
    """
    if not isinstance(hour, int) or not isinstance(minute, int):
        raise ValueError("ساعت محلی باید عدد صحیح باشد")
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"ساعت محلی نامعتبر است: {hour:02d}:{minute:02d}")
    try:
        jdatetime.date(year, month, day)
    except ValueError as exc:
        raise ValueError(f"تاریخ شمسی نامعتبر است: {year}-{month:02d}-{day:02d}") from exc

    stamp = (year, month, day, hour, minute)
    offset = OFFSET_0330
    rule = _baseline_rule(stamp)

    for transition in TRANSITIONS:
        if stamp < transition["start"]:
            break
        if stamp <= transition["end"]:
            if transition["kind"] == "gap":
                return _pack(transition["after"], "nonexistent", transition["resolution"], transition["rule"])
            return _pack(transition["before"], "ambiguous", transition["resolution"], transition["rule"])
        offset = transition["after"]
        rule = transition["after_rule"]

    return _pack(offset, "unique", "unique local time", rule)


def _gregorian_noon_offset(year, month, day):
    jalali = jdatetime.date.fromgregorian(year=year, month=month, day=day)
    return iran_offset_for_jalali(jalali.year, jalali.month, jalali.day, 12, 0)


def should_apply_dst(year, month, day):
    """Whether the seasonal extra hour is in effect at local noon on a Gregorian date."""
    return _gregorian_noon_offset(year, month, day)["dst_applied"]


def is_dst_active_in_year(year):
    """
    Whether 1 July of this Gregorian year falls in a Solar Hijri year whose
    summer carries the seasonal extra hour. 1 July is in Tir.
    """
    jalali = jdatetime.date.fromgregorian(year=year, month=7, day=1)
    info = iran_offset_for_jalali(jalali.year, jalali.month, jalali.day, 12, 0)
    return info["dst_applied"]


def get_dst_info(year):
    """Describe the offset at noon on 1 July, from ``iran_offset_for_jalali``."""
    info = _gregorian_noon_offset(year, 7, 1)
    jalali = jdatetime.date.fromgregorian(year=year, month=7, day=1)
    return {
        "year": year,
        "jalali_year": jalali.year,
        "dst_active": info["dst_applied"],
        "utc_offset": info["offset_str"],
        "reason": info["rule"],
    }


# Local noons where this table and current IANA tz main (Asia/Tehran) differ.
# Every other noon in the tests matches that zone. pytz 2024.1 is older;
# its two stale transitions are ``PYTZ_2024_1_OUTDATED``, not this list.
TZDATA_DISAGREEMENTS = (
    {
        "jalali": (1300, 1, 1),
        "offset": "+03:30",
        "note": "Before 22 Khordad 1314 (13 June 1935) tz main is local mean "
        "time +03:25:44. This table stays on +03:30 and does not model LMT.",
    },
    {
        "jalali": (1356, 1, 1),
        "offset": "+04:30",
        "note": "Owner decision: 1356 daylight time starts at 00:00 on "
        "1 Farvardin. tz main's 1977 rule is 23:00 on 21 March, so noon on "
        "1 Farvardin is still +03:30 there and +04:30 here. From 2 Farvardin "
        "the two agree at +04:30.",
    },
    {
        "jalali": (1357, 1, 4),
        "offset": "+05:00",
        "note": "Uncertain. Government notice used here: 00:00 on the first "
        "Friday of Farvardin (4 Farvardin 1357). tz main follows Kayhan and "
        "starts +05:00 at 24:00 at the end of 4 Farvardin, so this noon is "
        "still +04:00 there. From 5 Farvardin the two agree at +05:00.",
    },
    {
        "jalali": (1358, 6, 28),
        "offset": "+04:30",
        "note": "Uncertain. The cabinet decree used here ends daylight time "
        "at 24:00 on 30 Shahrivar 1358. tz main ends it at 24:00 on "
        "27 Shahrivar (18 September 1979), so 28–30 Shahrivar are +03:30 "
        "there and +04:30 here. 31 Shahrivar agrees at +03:30.",
    },
    {
        "jalali": (1371, 1, 1),
        "offset": "+04:30",
        "note": "Owner decision for every Farvardin-start year from 1371 "
        "through 1384 and 1387 through 1401: 00:00 at the start of "
        "1 Farvardin. The decree says 24:00 of 1 Farvardin, and tz main "
        "reads that as the end of the day, so noon on 1 Farvardin is +03:30 "
        "there and +04:30 here. 2 Farvardin and 30 Shahrivar agree; "
        "31 Shahrivar agrees at +03:30. Same one-day spring difference in "
        "1384, 1387, 1390 and 1401.",
    },
)


# Local noons where pytz 2024.1's bundled Asia/Tehran disagrees with current
# tz main. This table agrees with tz main on these noons. The values were
# read from pytz==2024.1; the Iran path does not import pytz.
PYTZ_2024_1_OUTDATED = (
    {
        "jalali": (1357, 8, 20),
        "pytz_offset": "+04:00",
        "note": "pytz 2024.1 keeps +04:00 until 24:00 on 31 December 1978. "
        "tz main and this table return to +03:30 at 24:00 on 19 Aban 1357 "
        "(10 November 1978).",
    },
    {
        "jalali": (1357, 10, 10),
        "pytz_offset": "+04:00",
        "note": "10 Dey 1357 is after 19 Aban, so it is +03:30 here. "
        "pytz 2024.1 is still +04:00 until the outdated 31 December transition.",
    },
    {
        "jalali": (1358, 3, 5),
        "pytz_offset": "+03:30",
        "note": "pytz 2024.1 starts 1358 daylight time at 01:00 on 27 May 1979 "
        "(6 Khordad). tz main and this table start at 00:00 on 26 May "
        "(5 Khordad).",
    },
)
