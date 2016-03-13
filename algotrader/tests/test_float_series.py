import datetime
from unittest import TestCase

from algotrader.trading.portfolio import FloatSeries


class FloatSeriesTest(TestCase):
    def test_size(self):
        series = FloatSeries()
        self.assertEqual(0, series.size())

        series.add(datetime.datetime.now(), 1)
        self.assertEqual(1, series.size())

        series.add(datetime.datetime.now(), 1)
        self.assertEqual(2, series.size())

    def test_get_current_value(self):
        series = FloatSeries()
        self.assertEqual(0, series.current_value())

        series.add(datetime.datetime.now(), 2)
        self.assertEqual(2, series.current_value())

        series.add(datetime.datetime.now(), 2.4)
        self.assertEqual(2.4, series.current_value())

    def test_get_value(self):
        series = FloatSeries()

        series.add(datetime.datetime.now(), 2)
        series.add(datetime.datetime.now(), 2.4)

        self.assertEqual(2, series.get_value(0))

        self.assertEqual(2.4, series.get_value(1))
