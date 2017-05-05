from unittest import TestCase

from algotrader.utils.market_data import *


class BarTest(TestCase):
    current_dt = datetime.datetime(year=2016, month=8, day=1, hour=6, minute=3, second=4)
    current_ts = datetime_to_unixtimemillis(current_dt)

    def ts(self, func, size):
        return func(BarTest.current_ts, size)

    def expected(self, year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None):
        year = year if year is not None and year >= 0 else BarTest.current_dt.year
        month = month if month is not None and month >= 0 else BarTest.current_dt.month
        day = day if day is not None and day >= 0 else BarTest.current_dt.day
        hour = hour if hour is not None and hour >= 0 else BarTest.current_dt.hour
        minute = minute if minute is not None and minute >= 0 else BarTest.current_dt.minute
        second = second if second is not None and second >= 0 else BarTest.current_dt.second
        microsecond = microsecond if microsecond is not None and microsecond >= 0 else BarTest.current_dt.microsecond

        return datetime_to_unixtimemillis(
            datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                              microsecond=microsecond))

    def test_current_bar_start_time(self):
        func = get_current_bar_start_time

        self.assertEqual(self.expected(second=4), self.ts(func, S1))

        self.assertEqual(self.expected(second=0, microsecond=0), self.ts(func, S5))

        self.assertEqual(self.expected(second=0, microsecond=0), self.ts(func, S15))

        self.assertEqual(self.expected(second=0, microsecond=0), self.ts(func, S30))

        self.assertEqual(self.expected(second=0, microsecond=0), self.ts(func, M1))

        self.assertEqual(self.expected(minute=0, second=0, microsecond=0), self.ts(func, M5))

        self.assertEqual(self.expected(minute=0, second=0, microsecond=0), self.ts(func, M15))

        self.assertEqual(self.expected(minute=0, second=0, microsecond=0), self.ts(func, M30))

        self.assertEqual(self.expected(minute=0, second=0, microsecond=0), self.ts(func, H1))

        self.assertEqual(self.expected(hour=0, minute=0, second=0, microsecond=0), self.ts(func, D1))

    def test_current_bar_end_time(self):
        func = get_current_bar_end_time

        self.assertEqual(self.expected(second=4, microsecond=999999), self.ts(func, S1))

        self.assertEqual(self.expected(second=4, microsecond=999999), self.ts(func, S5))

        self.assertEqual(self.expected(second=14, microsecond=999999), self.ts(func, S15))

        self.assertEqual(self.expected(second=29, microsecond=999999), self.ts(func, S30))

        self.assertEqual(self.expected(second=59, microsecond=999999), self.ts(func, M1))

        self.assertEqual(self.expected(minute=4, second=59, microsecond=999999), self.ts(func, M5))

        self.assertEqual(self.expected(minute=14, second=59, microsecond=999999), self.ts(func, M15))

        self.assertEqual(self.expected(minute=29, second=59, microsecond=999999), self.ts(func, M30))

        self.assertEqual(self.expected(minute=59, second=59, microsecond=999999), self.ts(func, H1))

        self.assertEqual(self.expected(hour=23, minute=59, second=59, microsecond=999999), self.ts(func, D1))

    def test_next_bar_start_time(self):
        func = get_next_bar_start_time

        self.assertEqual(self.expected(second=5, microsecond=0), self.ts(func, S1))

        self.assertEqual(self.expected(second=5, microsecond=0), self.ts(func, S5))

        self.assertEqual(self.expected(second=15, microsecond=0), self.ts(func, S15))

        self.assertEqual(self.expected(second=30, microsecond=0), self.ts(func, S30))

        self.assertEqual(self.expected(minute=4, second=0, microsecond=0), self.ts(func, M1))

        self.assertEqual(self.expected(minute=5, second=0, microsecond=0), self.ts(func, M5))

        self.assertEqual(self.expected(minute=15, second=0, microsecond=0), self.ts(func, M15))

        self.assertEqual(self.expected(minute=30, second=0, microsecond=0), self.ts(func, M30))

        self.assertEqual(self.expected(hour=7, minute=0, second=0, microsecond=0), self.ts(func, H1))

        self.assertEqual(self.expected(day=2, hour=0, minute=0, second=0, microsecond=0), self.ts(func, D1))
