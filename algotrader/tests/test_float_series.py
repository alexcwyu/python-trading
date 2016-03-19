import datetime
from unittest import TestCase

from algotrader.utils.time_series import TimeSeries


class FloatSeriesTest(TestCase):
    def test_size(self):
        series = TimeSeries()
        self.assertEqual(0, series.size())

        series.add(datetime.datetime.now(), 1)
        self.assertEqual(1, series.size())

        series.add(datetime.datetime.now(), 1)
        self.assertEqual(2, series.size())

    def test_get_current_value(self):
        series = TimeSeries()
        self.assertEqual(0, series.current_value())

        series.add(datetime.datetime.now(), 2)
        self.assertEqual(2, series.current_value())

        series.add(datetime.datetime.now(), 2.4)
        self.assertEqual(2.4, series.current_value())

    def test_get_value_by_index(self):
        series = TimeSeries()

        series.add(datetime.datetime.now(), 2)
        series.add(datetime.datetime.now(), 2.4)

        self.assertEqual(2, series.get_value_by_idx(0))

        self.assertEqual(2.4, series.get_value_by_idx(1))

    def test_get_value_by_time(self):
        series = TimeSeries()

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        series.add(t1, 2)
        series.add(t2, 2.4)

        self.assertEqual(2, series.get_value_by_time(t1))

        self.assertEqual(2.4, series.get_value_by_time(t2))