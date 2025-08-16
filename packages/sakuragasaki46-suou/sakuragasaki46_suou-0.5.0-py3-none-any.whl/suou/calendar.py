"""
Calendar utilities (mainly Gregorian oof)

---

Copyright (c) 2025 Sakuragasaki46.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
See LICENSE for the specific language governing permissions and
limitations under the License.

This software is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""


import datetime

from suou.functools import not_implemented


def want_isodate(d: datetime.datetime | str | float | int, *, tz = None) -> str:
    """
    Convert a date into ISO timestamp (e.g. 2020-01-01T02:03:04)
    """
    if isinstance(d, (int, float)):
        d = datetime.datetime.fromtimestamp(d, tz=tz)
    if isinstance(d, str):
        return d
    return d.isoformat()


def want_datetime(d: datetime.datetime | str | float | int, *, tz = None) -> datetime.datetime:
    """
    Convert a date into Python datetime.datetime (e.g. datetime.datetime(2020, 1, 1, 2, 3, 4)).

    If a string is passed, ISO format is assumed
    """
    if isinstance(d, str):
        d = datetime.datetime.fromisoformat(d)
    elif isinstance(d, (int, float)):
        d = datetime.datetime.fromtimestamp(d, tz=tz)
    return d

def want_timestamp(d: datetime.datetime | str | float | int, *, tz = None) -> float:
    """
    Convert a date into UNIX timestamp (e.g. 1577840584.0). Returned as a float; decimals are milliseconds.
    """
    if isinstance(d, str):
        d = want_datetime(d, tz=tz)
    if isinstance(d, (int, float)):
        return d
    return d.timestamp()

def age_and_days(date: datetime.datetime, now: datetime.datetime | None = None) -> tuple[int, int]:
    """
    Compute age / duration of a timespan in years and days.
    """
    if now is None:
        now = datetime.date.today()
    y = now.year - date.year - ((now.month, now.day) < (date.month, date.day))
    d = (now - datetime.date(date.year + y, date.month, date.day)).days
    return y, d

__all__ = ('want_datetime', 'want_timestamp', 'want_isodate', 'age_and_days')