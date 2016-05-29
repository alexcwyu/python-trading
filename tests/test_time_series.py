import datetime
import math
from unittest import TestCase

import numpy as np

from algotrader.utils.time_series import TimeSeries


class TimeSeriesTest(TestCase):
    def test_size(self):
        series = TimeSeries()
        self.assertEqual(0, series.size())

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        series.add(t1, 1)
        self.assertEqual(1, series.size())

        series.add(t2, 1)
        self.assertEqual(2, series.size())

    def test_get_current_value(self):
        series = TimeSeries()
        self.assertTrue(math.isnan(series.now()))

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        series.add(t1, 2)
        self.assertEqual(2, series.now())

        series.add(t2, 2.4)
        self.assertEqual(2.4, series.now())

    def test_get_value_by_index(self):
        series = TimeSeries()

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        series.add(t1, 2)
        series.add(t2, 2.4)

        self.assertEqual(2, series.get_by_idx(0))

        self.assertEqual(2.4, series.get_by_idx(1))

    def test_get_value_by_time(self):
        series = TimeSeries()

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        series.add(t1, 2)
        series.add(t2, 2.4)

        self.assertEqual(2, series.get_by_time(t1))

        self.assertEqual(2.4, series.get_by_time(t2))

    def test_override_w_same_time(self):
        series = TimeSeries()
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        self.assertEqual(0, series.size())

        series.add(t1, 2)
        self.assertEqual(1, series.size())
        self.assertEqual(2, series.get_by_idx(0))
        self.assertEqual(2, series.get_by_time(t1))

        series.add(t1, 2.4)
        self.assertEqual(1, series.size())
        self.assertEqual(2.4, series.get_by_idx(0))
        self.assertEqual(2.4, series.get_by_time(t1))
        self.assertEqual([2.4], series.get_by_idx())

        series.add(t2, 2.6)
        self.assertEqual(2, series.size())
        self.assertEqual(2.4, series.get_by_idx(0))
        self.assertEqual(2.4, series.get_by_time(t1))
        self.assertEqual(2.6, series.get_by_idx(1))
        self.assertEqual(2.6, series.get_by_time(t2))
        self.assertEqual([2.4, 2.6], series.get_by_idx())

    def __create_series(self):
        close = TimeSeries("close")

        t = datetime.datetime.now()

        values = [np.nan, np.nan, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
                  45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]

        for idx, value in enumerate(values):
            close.add(t, value)
            t = t + datetime.timedelta(0, 3)

        return close

    def test_subscript(self):
        close = self.__create_series()
        self.assertEquals([np.nan, np.nan], close[0:2])
        self.assertEquals([np.nan, np.nan, 44.34, 44.09], close[0:4])
        self.assertEquals([np.nan, np.nan, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83], close[0:8])
        self.assertEquals([45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.0], close[-8:])

    def test_mean(self):
        close = self.__create_series()
        self.assertAlmostEqual(45.2425, close.mean(-80))
        self.assertAlmostEqual(45.2425, close.mean())
        self.assertAlmostEqual(44.215, close.mean(0, 4))
        self.assertAlmostEqual(44.0475, close.mean(0, 6))

    def test_median(self):
        close = self.__create_series()
        self.assertAlmostEqual(45.515, close.median())
        self.assertAlmostEqual(44.215, close.median(0, 4))
        self.assertAlmostEqual(44.12, close.median(0, 6))

    def test_max(self):
        close = self.__create_series()
        self.assertAlmostEqual(46.28, close.max())
        self.assertAlmostEqual(44.34, close.max(0, 4))
        self.assertAlmostEqual(44.34, close.max(0, 6))

    def test_min(self):
        close = self.__create_series()
        self.assertAlmostEqual(43.61, close.min())
        self.assertAlmostEqual(44.09, close.min(0, 4))
        self.assertAlmostEqual(43.61, close.min(0, 6))

    def test_std(self):
        close = self.__create_series()
        self.assertAlmostEqual(0.866584531364, close.std())
        self.assertAlmostEqual(0.125, close.std(0, 4))
        self.assertAlmostEqual(0.268921456935, close.std(0, 6))

    def test_var(self):
        close = self.__create_series()
        self.assertAlmostEqual(0.75096875, close.var())
        self.assertAlmostEqual(0.015625, close.var(0, 4))
        self.assertAlmostEqual(0.07231875, close.var(0, 6))
