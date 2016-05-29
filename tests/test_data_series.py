import datetime
from unittest import TestCase

import numpy as np

from algotrader.utils.time_series import DataSeries


class DataSeriesTest(TestCase):
    def test_size(self):
        series = DataSeries()
        self.assertEqual({}, series.size())

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        series.add(t1, {"v1": 1})
        self.assertEqual({'v1': 1}, series.size())

        series.add(t2, {"v1": 1})
        self.assertEqual({'v1': 2}, series.size())
        self.assertEqual({'v1': 2}, series.size(["v1"]))
        self.assertEqual({'v1': 2, 'v2': 0}, series.size(["v1", "v2"]))

    def test_get_current_value(self):
        series = DataSeries()
        self.assertEqual({}, series.now())

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)
        t3 = t2 + datetime.timedelta(0, 3)

        series.add(t1, {"v1": 2})
        self.assertEqual({"v1": 2}, series.now())

        series.add(t2, {"v1": 2.4})
        self.assertEqual({"v1": 2.4}, series.now())

        series.add(t2, {"v2": 3.0})
        self.assertEqual({"v1": 2.4, "v2": 3.0}, series.now())
        self.assertEqual({"v1": 2.4}, series.now(["v1"]))
        self.assertEqual({"v1": 2.4, "v2": 3.0}, series.now(["v1", "v2"]))

    def test_get_value_by_index(self):
        series = DataSeries()

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        series.add(t1, {"v1": 2})
        series.add(t2, {"v1": 2.4})
        series.add(t2, {"v2": 3.0})

        self.assertEqual(2, series.get_by_idx("v1", idx=0))
        self.assertEqual(2.4, series.get_by_idx("v1", idx=1))
        self.assertEqual(3.0, series.get_by_idx("v2", idx=0))

    def test_get_value_by_time(self):
        series = DataSeries()

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        series.add(t1, {"v1": 2})
        series.add(t2, {"v1": 2.4})
        series.add(t2, {"v2": 3.0})

        self.assertEqual(2, series.get_by_time("v1", t1))
        self.assertEqual(2.4, series.get_by_time("v1", t2))
        self.assertEqual(3.0, series.get_by_time("v2", t2))

    def test_override_w_same_time(self):
        series = DataSeries()
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)


        series.add(t1,  {"v1": 2, "v2":3})
        self.assertEqual({"v1":1, "v2":1}, series.size())
        self.assertEqual(2, series.get_by_idx("v1", 0))
        self.assertEqual(2, series.get_by_time("v1", t1))

        series.add(t1, {"v1": 2.4, "v2":3.4, "v3":1.1})
        self.assertEqual({"v1":1, "v2":1, "v3":1}, series.size())
        self.assertEqual(2.4, series.get_by_idx("v1",0))
        self.assertEqual(2.4, series.get_by_time("v1", t1))
        self.assertEqual([2.4], series.get_by_idx("v1"))

        series.add(t2,  {"v1": 2.6, "v2":3.6})
        self.assertEqual({"v1":2, "v2":2, "v3":1}, series.size())
        self.assertEqual(2.4, series.get_by_idx("v1", 0))
        self.assertEqual(2.4, series.get_by_time("v1", t1))
        self.assertEqual(2.6, series.get_by_idx("v1", 1))
        self.assertEqual(2.6, series.get_by_time("v1", t2))
        self.assertEqual([2.4, 2.6], series.get_by_idx("v1"))

    def __create_series(self):
        close = DataSeries("close")

        t = datetime.datetime.now()

        values = [np.nan, np.nan, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
                  45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]

        for idx, value in enumerate(values):
            close.add(t, {"v1":value})
            t = t + datetime.timedelta(0, 3)

        return close

    def test_subscript(self):
        close = self.__create_series()
        self.assertEquals([np.nan, np.nan], close["v1",0:2])
        self.assertEquals([np.nan, np.nan, 44.34, 44.09], close["v1",0:4])
        self.assertEquals([np.nan, np.nan, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83], close["v1",0:8])
        self.assertEquals([45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.0], close["v1",-8:])

    def test_mean(self):
        close = self.__create_series()
        self.assertAlmostEqual(45.2425, close.mean(start=-80)["v1"])
        self.assertAlmostEqual(45.2425, close.mean()["v1"])
        self.assertAlmostEqual(44.215, close.mean(start=0, end=4)["v1"])
        self.assertAlmostEqual(44.0475, close.mean(start=0, end=6)["v1"])

    def test_median(self):
        close = self.__create_series()
        self.assertAlmostEqual(45.515, close.median()["v1"])
        self.assertAlmostEqual(44.215, close.median(start=0, end=4)["v1"])
        self.assertAlmostEqual(44.12, close.median(start=0, end=6)["v1"])

    def test_max(self):
        close = self.__create_series()
        self.assertAlmostEqual(46.28, close.max()["v1"])
        self.assertAlmostEqual(44.34, close.max(start=0, end=4)["v1"])
        self.assertAlmostEqual(44.34, close.max(start=0, end=6)["v1"])

    def test_min(self):
        close = self.__create_series()
        self.assertAlmostEqual(43.61, close.min()["v1"])
        self.assertAlmostEqual(44.09, close.min(start=0, end=4)["v1"])
        self.assertAlmostEqual(43.61, close.min(start=0, end=6)["v1"])

    def test_std(self):
        close = self.__create_series()
        self.assertAlmostEqual(0.866584531364, close.std()["v1"])
        self.assertAlmostEqual(0.125, close.std(start=0, end=4)["v1"])
        self.assertAlmostEqual(0.268921456935, close.std(start=0, end=6)["v1"])

    def test_var(self):
        close = self.__create_series()
        self.assertAlmostEqual(0.75096875, close.var()["v1"])
        self.assertAlmostEqual(0.015625, close.var(start=0, end=4)["v1"])
        self.assertAlmostEqual(0.07231875, close.var(start=0, end=6)["v1"])
