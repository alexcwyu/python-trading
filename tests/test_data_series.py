import datetime
from unittest import TestCase

import numpy as np

from algotrader.utils.time_series import DataSeries


class DataSeriesTest(TestCase):

    def test_init_w_data(self):

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        data_list= [{"timestamp": t1, "v1": 1}, {"timestamp": t2, "v1": 2}]

        series = DataSeries(keys = set(["timestamp", "v1"]), data_list=data_list)

        self.assertEqual(2, series.size())

        result = series.get_data()

        self.assertEqual(2, len(result["v1"]))
        self.assertEqual(1, result["v1"][t1])
        self.assertEqual(2, result["v1"][t2])


    def test_init_w_keys(self):
        series = DataSeries(keys = set(["timestamp", "v1"]))

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)
        series.add({"timestamp": t1, "v1": 1, "v2": 1})

        result = series.get_data()
        self.assertTrue("timestamp" in result)
        self.assertTrue("v1" in result)
        self.assertFalse("v2" in result)


    def test_size(self):
        series = DataSeries()
        self.assertEqual(0, series.size())

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        series.add({"timestamp": t1, "v1": 1})
        self.assertEqual(1, series.size())

        series.add({"timestamp": t2, "v1": 1})
        self.assertEqual(2, series.size())

    def test_now(self):
        series = DataSeries()
        self.assertTrue(np.isnan(series.now()))

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)
        t3 = t2 + datetime.timedelta(0, 3)
        t4 = t3 + datetime.timedelta(0, 3)

        series.add({"timestamp": t1, "v1": 1, "v2": 2})
        self.assertEqual({"timestamp": t1, "v1": 1, "v2": 2}, series.now())

        series.add({"timestamp": t2, "v1": 1.2, "v2": 2.2})
        self.assertEqual({"timestamp": t2, "v1": 1.2, "v2": 2.2}, series.now())

        series.add({"timestamp": t3, "v1": 1.3, "v2": 2.3})
        series.add({"timestamp": t4, "v1": 1.4, "v2": 2.4})

        self.assertEqual({"timestamp": t4, "v1": 1.4, "v2": 2.4}, series.now())
        self.assertEqual(1.4, series.now(["v1"]))
        self.assertEqual({ "v1": 1.4, "v2": 2.4}, series.now(["v1", "v2"]))


    def test_ago(self):
        series = DataSeries()
        self.assertTrue(np.isnan(series.now()))

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)
        t3 = t2 + datetime.timedelta(0, 3)
        t4 = t3 + datetime.timedelta(0, 3)

        series.add({"timestamp": t1, "v1": 1, "v2": 2})
        self.assertEqual({"timestamp": t1, "v1": 1, "v2": 2}, series.ago(0))

        series.add({"timestamp": t2, "v1": 1.2, "v2": 2.2})
        self.assertEqual({"timestamp": t2, "v1": 1.2, "v2": 2.2}, series.ago(0))
        self.assertEqual({"timestamp": t1, "v1": 1, "v2": 2}, series.ago(1))

        series.add({"timestamp": t3, "v1": 1.3, "v2": 2.3})
        self.assertEqual({"timestamp": t3, "v1": 1.3, "v2": 2.3}, series.ago(0))
        self.assertEqual({"timestamp": t2, "v1": 1.2, "v2": 2.2}, series.ago(1))
        self.assertEqual({"timestamp": t1, "v1": 1, "v2": 2}, series.ago(2))


        series.add({"timestamp": t4, "v1": 1.4, "v2": 2.4})
        self.assertEqual({"timestamp": t4, "v1": 1.4, "v2": 2.4}, series.ago(0))
        self.assertEqual({"timestamp": t3, "v1": 1.3, "v2": 2.3}, series.ago(1))
        self.assertEqual({"timestamp": t2, "v1": 1.2, "v2": 2.2}, series.ago(2))
        self.assertEqual({"timestamp": t1, "v1": 1, "v2": 2}, series.ago(3))


        self.assertEqual({"v1": 1.4, "v2": 2.4}, series.ago(0, ["v1", "v2"]))
        self.assertEqual(1.4, series.ago(0, "v1"))
        self.assertEqual(1.4, series.ago(0, ["v1"]))

    def test_get_value_by_index(self):
        series = DataSeries(keys = set(["timestamp", "v1", "v2"]))

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)

        series.add({"timestamp": t1, "v1": 2})
        series.add({"timestamp": t2, "v1": 2.4})
        series.add({"timestamp": t2, "v2": 3.0})

        # index and key
        self.assertEqual(2, series.get_by_idx(idx=0, keys="v1"))
        self.assertTrue(np.isnan(series.get_by_idx(idx=0, keys="v2")))
        self.assertEqual(2.4, series.get_by_idx(idx=1, keys="v1"))
        self.assertEqual(3.0, series.get_by_idx(idx=1, keys="v2"))

        # index only
        self.assertEqual({"timestamp": t1, "v1": 2, "v2" : np.nan}, series.get_by_idx(idx=0))
        self.assertEqual({"timestamp": t2, "v1": 2.4, "v2" : 3.0}, series.get_by_idx(idx=1))

    def test_get_value_by_time(self):
        series = DataSeries(keys = set(["timestamp", "v1", "v2"]))

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)


        # time and key
        series.add({"timestamp": t1, "v1": 2})
        series.add({"timestamp": t2, "v1": 2.4})
        series.add({"timestamp": t2, "v2": 3.0})

        self.assertEqual(2, series.get_by_time(time=t1, keys="v1"))
        self.assertTrue(np.isnan(series.get_by_time(time=t1, keys="v2")))
        self.assertEqual(2.4, series.get_by_time(time=t2, keys="v1"))
        self.assertEqual(3.0, series.get_by_time(time=t2, keys="v2"))
        # time only
        self.assertEqual({"timestamp": t1, "v1": 2, "v2" : np.nan}, series.get_by_time(time=t1))
        self.assertEqual({"timestamp": t2, "v1": 2.4, "v2" : 3.0}, series.get_by_time(time=t2))

    def test_override_w_same_time(self):
        series = DataSeries(keys = set(["timestamp", "v1", "v2", "v3"]))
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)


        series.add({"timestamp": t1, "v1": 2, "v2":3})
        self.assertEqual(1, series.size())
        self.assertEqual(2, series.get_by_idx( 0, "v1"))
        self.assertEqual(2, series.get_by_time(t1, "v1"))
        self.assertEqual(3, series.get_by_idx( 0, "v2"))
        self.assertEqual(3, series.get_by_time(t1, "v2"))
        self.assertTrue(np.isnan(series.get_by_idx( 0, "v3")))
        self.assertTrue(np.isnan(series.get_by_time(t1, "v3")))

        series.add({"timestamp": t1, "v1": 2.4, "v2":3.4, "v3":1.1})
        self.assertEqual(1, series.size())
        self.assertEqual(2.4, series.get_by_idx(0, "v1"))
        self.assertEqual(2.4, series.get_by_time(t1,"v1"))
        self.assertEqual(3.4, series.get_by_idx(0, "v2"))
        self.assertEqual(3.4, series.get_by_time(t1,"v2"))
        self.assertEqual(1.1, series.get_by_idx(0, "v3"))
        self.assertEqual(1.1, series.get_by_time(t1,"v3"))

        series.add({"timestamp": t2, "v1": 2.6, "v2":3.6})
        self.assertEqual(2, series.size())
        self.assertEqual(2.4, series.get_by_idx(0, "v1"))
        self.assertEqual(2.4, series.get_by_time(t1,"v1"))
        self.assertEqual(3.4, series.get_by_idx(0, "v2"))
        self.assertEqual(3.4, series.get_by_time(t1,"v2"))
        self.assertEqual(1.1, series.get_by_idx(0, "v3"))
        self.assertEqual(1.1, series.get_by_time(t1,"v3"))

        self.assertEqual(2.6, series.get_by_idx(1, "v1"))
        self.assertEqual(2.6, series.get_by_time(t2,"v1"))
        self.assertEqual(3.6, series.get_by_idx(1, "v2"))
        self.assertEqual(3.6, series.get_by_time(t2,"v2"))
        self.assertTrue(np.isnan(series.get_by_idx(1, "v3")))
        self.assertTrue(np.isnan(series.get_by_time(t2,"v3")))



    def __create_series(self):
        close = DataSeries("close")

        t = datetime.datetime.now()

        values = [np.nan, np.nan, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
                  45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]

        for idx, value in enumerate(values):
            close.add({"timestamp": t, "v1":value})
            t = t + datetime.timedelta(0, 3)

        return close

    def test_subscript(self):
        close = self.__create_series()
        self.assertEquals([np.nan, np.nan], close[0:2, "v1"])
        self.assertEquals([np.nan, np.nan, 44.34, 44.09], close[0:4, "v1"])
        self.assertEquals([np.nan, np.nan, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83], close[0:8, "v1"])
        self.assertEquals([45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.0], close[-8:, "v1"])

    def test_mean(self):
        close = self.__create_series()
        self.assertAlmostEqual(45.2425, close.mean(start=-80, keys="v1"))
        self.assertAlmostEqual(45.2425, close.mean(keys="v1"))
        self.assertAlmostEqual(44.215, close.mean(start=0, end=4, keys="v1"))
        self.assertAlmostEqual(44.0475, close.mean(start=0, end=6, keys="v1"))

    def test_median(self):
        close = self.__create_series()
        self.assertAlmostEqual(45.515, close.median(keys="v1"))
        self.assertAlmostEqual(44.215, close.median(start=0, end=4, keys="v1"))
        self.assertAlmostEqual(44.12, close.median(start=0, end=6, keys="v1"))

    def test_max(self):
        close = self.__create_series()
        self.assertAlmostEqual(46.28, close.max(keys="v1"))
        self.assertAlmostEqual(44.34, close.max(start=0, end=4, keys="v1"))
        self.assertAlmostEqual(44.34, close.max(start=0, end=6, keys="v1"))

    def test_min(self):
        close = self.__create_series()
        self.assertAlmostEqual(43.61, close.min(keys="v1"))
        self.assertAlmostEqual(44.09, close.min(start=0, end=4, keys="v1"))
        self.assertAlmostEqual(43.61, close.min(start=0, end=6, keys="v1"))

    def test_std(self):
        close = self.__create_series()
        self.assertAlmostEqual(0.866584531364, close.std(keys="v1"))
        self.assertAlmostEqual(0.125, close.std(start=0, end=4, keys="v1"))
        self.assertAlmostEqual(0.268921456935, close.std(start=0, end=6, keys="v1"))

    def test_var(self):
        close = self.__create_series()
        self.assertAlmostEqual(0.75096875, close.var(keys="v1"))
        self.assertAlmostEqual(0.015625, close.var(start=0, end=4, keys="v1"))
        self.assertAlmostEqual(0.07231875, close.var(start=0, end=6, keys="v1"))
