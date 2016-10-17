import datetime
from unittest import TestCase

import numpy as np
import pandas as pd

from algotrader.utils.time_series import DataSeries


class DataSeriesTest(TestCase):
    t1 = datetime.datetime(2000, 1, 1, 11, 34, 59)
    t2 = t1 + datetime.timedelta(0, 3)
    t3 = t2 + datetime.timedelta(0, 3)
    t4 = t3 + datetime.timedelta(0, 3)
    values = [np.nan, np.nan, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
              45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]

    def __create_series(self):
        close = DataSeries("close")

        t = self.t1
        for idx, value in enumerate(self.values):
            close.add({"timestamp": t, "v1": value, "v2": value})
            t = t + datetime.timedelta(0, 3)

        return close

    @staticmethod
    def create_random_walk_series():
        close = DataSeries("close")

        t1 = datetime.datetime(2000, 1, 1, 11, 34, 59)
        t = t1
        w = np.random.normal(0, 1, 1000)
        xs = 100 + np.cumsum(w)

        for value in xs:
            close.add({"timestamp": t, "v1": value, "v2": value})
            t = t + datetime.timedelta(0, 3)
        return close

    @staticmethod
    def create_series_by_list(valuelist):
        close = DataSeries("close")

        t = datetime.datetime(2000, 1, 1, 11, 34, 59)

        for value in valuelist:
            close.add({"timestamp": t, "v1": value})
            t = t + datetime.timedelta(0, 3)
        return close

    def test_init_w_data(self):

        data_list = [{"timestamp": self.t1, "v1": 1}, {"timestamp": self.t2, "v1": 2}]

        series = DataSeries(keys=set(["timestamp", "v1"]), data_list=data_list)

        self.assertEqual(2, series.size())

        result = series.get_data()

        self.assertEqual(2, len(result))
        self.assertEqual(1, result[0]["v1"])
        self.assertEqual(2, result[1]["v1"])

    def test_init_w_keys(self):
        series = DataSeries(keys=set(["timestamp", "v1"]))

        series.add({"timestamp": self.t1, "v1": 1, "v2": 1})

        result = series.get_data()

        self.assertEqual(1, len(result))
        self.assertTrue("timestamp" in result[0])
        self.assertTrue("v1" in result[0])
        self.assertFalse("v2" in result[0])

    def test_add(self):
        series = DataSeries()

        self.assertTrue(len(series.get_data()) == 0)

        series.add({"timestamp": self.t1, "v1": 1, "v2": 1})
        series.add({"timestamp": self.t2, "v1": 2, "v2": 2})

        self.assertEqual([{'name': "'None'", "timestamp": self.t1, "v1": 1, "v2": 1},
                          {'name': "'None'", "timestamp": self.t2, "v1": 2, "v2": 2}], series.get_data())

        series.add({"timestamp": self.t2, "v1": 3, "v2": 3})

        self.assertEqual([{'name': "'None'", "timestamp": self.t1, "v1": 1, "v2": 1},
                          {'name': "'None'", "timestamp": self.t2, "v1": 3, "v2": 3}], series.get_data())

        series.add({"timestamp": self.t3, "v1": 4, "v2": 4})

        self.assertEqual([{'name': "'None'", "timestamp": self.t1, "v1": 1, "v2": 1},
                          {'name': "'None'", "timestamp": self.t2, "v1": 3, "v2": 3},
                          {'name': "'None'", "timestamp": self.t3, "v1": 4, "v2": 4}], series.get_data())

    def test_current_time(self):
        series = DataSeries()
        self.assertEqual(None, series.current_time())

        series.add({"timestamp": self.t1, "v1": 1, "v2": 1})
        self.assertEqual(self.t1, series.current_time())

        series.add({"timestamp": self.t1, "v1": 1, "v2": 1})
        self.assertEqual(self.t1, series.current_time())

        series.add({"timestamp": self.t2, "v1": 2, "v2": 2})
        self.assertEqual(self.t2, series.current_time())

    def test_get_data_dict(self):
        series = DataSeries()

        series.add({"timestamp": self.t1, "v1": 1, "v2": 1})
        series.add({"timestamp": self.t2, "v1": 2, "v2": 2})

        self.assertEqual({'name': {str(self.t1): "'None'",  str(self.t2): "'None'"},
                          "timestamp": {str(self.t1): self.t1, str(self.t2): self.t2},
                          "v1": {str(self.t1): 1, str(self.t2): 2},
                          "v2": {str(self.t1): 1, str(self.t2): 2}}, series.get_data_dict())

        self.assertEqual({"v1": {str(self.t1): 1, str(self.t2): 2}, "v2": {str(self.t1): 1, str(self.t2): 2}},
                         series.get_data_dict(['v1', 'v2']))
        self.assertEqual({str(self.t1): 1, str(self.t2): 2}, series.get_data_dict('v1'))

    def test_get_data(self):
        series = DataSeries()

        series.add({"timestamp": self.t1, "v1": 1, "v2": 1})
        series.add({"timestamp": self.t2, "v1": 2, "v2": 2})

        self.assertEqual([{'name': "'None'", "timestamp": self.t1, "v1": 1, "v2": 1},
                          {'name': "'None'", "timestamp": self.t2, "v1": 2, "v2": 2}], series.get_data())

    def test_get_series(self):

        close = self.__create_series()

        t = self.t1
        time_idx = []
        for idx, value in enumerate(self.values):
            time_idx.append(t)
            t = t + datetime.timedelta(0, 3)

        v1 = pd.Series(self.values, index=time_idx, name='v1')
        v2 = pd.Series(self.values, index=time_idx, name='v2')

        self.assertTrue(v1.equals(close.get_series('v1')))

        result = close.get_series(['v1', 'v2'])
        self.assertTrue(len(result) == 2)
        self.assertTrue(v1.equals(result['v1']))
        self.assertTrue(v2.equals(result['v2']))

    def test_get_data_frame(self):
        close = self.__create_series()

        t = self.t1
        time_idx = []
        for idx, value in enumerate(self.values):
            time_idx.append(t)
            t = t + datetime.timedelta(0, 3)

        v1 = pd.Series(self.values, index=time_idx, name='v1')
        v2 = pd.Series(self.values, index=time_idx, name='v2')

        df1 = pd.DataFrame({'v1': v1})
        df2 = pd.DataFrame({'v1': v1, 'v2': v2})

        self.assertTrue(df1.equals(close.get_data_frame('v1')))
        self.assertTrue(df2.equals(close.get_data_frame(['v1', 'v2'])))

    def test_size(self):
        series = DataSeries()
        self.assertEqual(0, series.size())

        series.add({"timestamp": self.t1, "v1": 1})
        self.assertEqual(1, series.size())

        series.add({"timestamp": self.t2, "v1": 1})
        self.assertEqual(2, series.size())

    def test_now(self):
        series = DataSeries()
        self.assertTrue(np.isnan(series.now()))

        series.add({"timestamp": self.t1, "v1": 1, "v2": 2})
        self.assertEqual({'name': "'None'", "timestamp": self.t1, "v1": 1, "v2": 2}, series.now())

        series.add({"timestamp": self.t2, "v1": 1.2, "v2": 2.2})
        self.assertEqual({'name': "'None'", "timestamp": self.t2, "v1": 1.2, "v2": 2.2}, series.now())

        series.add({"timestamp": self.t3, "v1": 1.3, "v2": 2.3})
        series.add({"timestamp": self.t4, "v1": 1.4, "v2": 2.4})

        self.assertEqual({'name': "'None'", "timestamp": self.t4, "v1": 1.4, "v2": 2.4}, series.now())
        self.assertEqual(1.4, series.now(["v1"]))
        self.assertEqual({"v1": 1.4, "v2": 2.4}, series.now(["v1", "v2"]))

    def test_ago(self):
        series = DataSeries()
        self.assertTrue(np.isnan(series.now()))

        series.add({"timestamp": self.t1, "v1": 1, "v2": 2})
        self.assertEqual({'name': "'None'", "timestamp": self.t1, "v1": 1, "v2": 2}, series.ago(0))

        series.add({"timestamp": self.t2, "v1": 1.2, "v2": 2.2})
        self.assertEqual({'name': "'None'", "timestamp": self.t2, "v1": 1.2, "v2": 2.2}, series.ago(0))
        self.assertEqual({'name': "'None'", "timestamp": self.t1, "v1": 1, "v2": 2}, series.ago(1))

        series.add({"timestamp": self.t3, "v1": 1.3, "v2": 2.3})
        self.assertEqual({'name': "'None'", "timestamp": self.t3, "v1": 1.3, "v2": 2.3}, series.ago(0))
        self.assertEqual({'name': "'None'", "timestamp": self.t2, "v1": 1.2, "v2": 2.2}, series.ago(1))
        self.assertEqual({'name': "'None'", "timestamp": self.t1, "v1": 1, "v2": 2}, series.ago(2))

        series.add({"timestamp": self.t4, "v1": 1.4, "v2": 2.4})
        self.assertEqual({'name': "'None'", "timestamp": self.t4, "v1": 1.4, "v2": 2.4}, series.ago(0))
        self.assertEqual({'name': "'None'", "timestamp": self.t3, "v1": 1.3, "v2": 2.3}, series.ago(1))
        self.assertEqual({'name': "'None'", "timestamp": self.t2, "v1": 1.2, "v2": 2.2}, series.ago(2))
        self.assertEqual({'name': "'None'", "timestamp": self.t1, "v1": 1, "v2": 2}, series.ago(3))

        self.assertEqual({"v1": 1.4, "v2": 2.4}, series.ago(0, ["v1", "v2"]))
        self.assertEqual(1.4, series.ago(0, "v1"))
        self.assertEqual(1.4, series.ago(0, ["v1"]))

    def test_get_by_idx(self):
        series = DataSeries(keys=set(["timestamp", "v1", "v2"]))

        series.add({"timestamp": self.t1, "v1": 2})
        series.add({"timestamp": self.t2, "v1": 2.4})
        series.add({"timestamp": self.t2, "v2": 3.0})

        # index and key
        self.assertEqual(2, series.get_by_idx(idx=0, keys="v1"))
        self.assertTrue(np.isnan(series.get_by_idx(idx=0, keys="v2")))
        self.assertEqual(2.4, series.get_by_idx(idx=1, keys="v1"))
        self.assertEqual(3.0, series.get_by_idx(idx=1, keys="v2"))

        # index only
        self.assertEqual({"timestamp": self.t1, "v1": 2, "v2": np.nan}, series.get_by_idx(idx=0))
        self.assertEqual({"timestamp": self.t2, "v1": 2.4, "v2": 3.0}, series.get_by_idx(idx=1))

        # test index slice
        series2 = self.create_series_by_list(range(100))
        sliced = series2.get_by_idx(keys='v1', idx=slice(-10,None,None))
        self.assertEqual(len(sliced), 10)

        endPoint = series2.get_by_idx(keys='v1', idx=slice(-1, None, None))
        self.assertEqual(endPoint[0], 99)


    def test_get_by_time(self):
        series = DataSeries(keys=set(["timestamp", "v1", "v2"]))

        # time and key
        series.add({"timestamp": self.t1, "v1": 2})
        series.add({"timestamp": self.t2, "v1": 2.4})
        series.add({"timestamp": self.t2, "v2": 3.0})

        self.assertEqual(2, series.get_by_time(time=self.t1, keys="v1"))
        self.assertTrue(np.isnan(series.get_by_time(time=self.t1, keys="v2")))
        self.assertEqual(2.4, series.get_by_time(time=self.t2, keys="v1"))
        self.assertEqual(3.0, series.get_by_time(time=self.t2, keys="v2"))
        # time only
        self.assertEqual({"timestamp": self.t1, "v1": 2, "v2": np.nan}, series.get_by_time(time=self.t1))
        self.assertEqual({"timestamp": self.t2, "v1": 2.4, "v2": 3.0}, series.get_by_time(time=self.t2))

    def test_override_w_same_time(self):
        series = DataSeries(keys=set(["timestamp", "v1", "v2", "v3"]))

        series.add({"timestamp": self.t1, "v1": 2, "v2": 3})
        self.assertEqual(1, series.size())
        self.assertEqual(2, series.get_by_idx(0, "v1"))
        self.assertEqual(2, series.get_by_time(self.t1, "v1"))
        self.assertEqual(3, series.get_by_idx(0, "v2"))
        self.assertEqual(3, series.get_by_time(self.t1, "v2"))
        self.assertTrue(np.isnan(series.get_by_idx(0, "v3")))
        self.assertTrue(np.isnan(series.get_by_time(self.t1, "v3")))

        series.add({"timestamp": self.t1, "v1": 2.4, "v2": 3.4, "v3": 1.1})
        self.assertEqual(1, series.size())
        self.assertEqual(2.4, series.get_by_idx(0, "v1"))
        self.assertEqual(2.4, series.get_by_time(self.t1, "v1"))
        self.assertEqual(3.4, series.get_by_idx(0, "v2"))
        self.assertEqual(3.4, series.get_by_time(self.t1, "v2"))
        self.assertEqual(1.1, series.get_by_idx(0, "v3"))
        self.assertEqual(1.1, series.get_by_time(self.t1, "v3"))

        series.add({"timestamp": self.t2, "v1": 2.6, "v2": 3.6})
        self.assertEqual(2, series.size())
        self.assertEqual(2.4, series.get_by_idx(0, "v1"))
        self.assertEqual(2.4, series.get_by_time(self.t1, "v1"))
        self.assertEqual(3.4, series.get_by_idx(0, "v2"))
        self.assertEqual(3.4, series.get_by_time(self.t1, "v2"))
        self.assertEqual(1.1, series.get_by_idx(0, "v3"))
        self.assertEqual(1.1, series.get_by_time(self.t1, "v3"))

        self.assertEqual(2.6, series.get_by_idx(1, "v1"))
        self.assertEqual(2.6, series.get_by_time(self.t2, "v1"))
        self.assertEqual(3.6, series.get_by_idx(1, "v2"))
        self.assertEqual(3.6, series.get_by_time(self.t2, "v2"))
        self.assertTrue(np.isnan(series.get_by_idx(1, "v3")))
        self.assertTrue(np.isnan(series.get_by_time(self.t2, "v3")))

    def test_subscript(self):
        close = self.__create_series()
        self.assertEquals([np.nan, np.nan], close[0:2, "v1"])
        self.assertEquals({"v1": [np.nan, np.nan, 44.34, 44.09], "v2": [np.nan, np.nan, 44.34, 44.09]},
                          close[0:4, ["v1", "v2"]])

        self.assertEquals([np.nan, np.nan, 44.34, 44.09], close[0:4, "v1"])
        self.assertEquals([np.nan, np.nan, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83], close[0:8, "v1"])
        self.assertEquals([45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.0], close[-8:, "v1"])

    def test_mean(self):
        close = self.__create_series()
        self.assertAlmostEqual(45.2425, close.mean(start=-80, keys="v1"))
        self.assertAlmostEqual({"v1": 45.2425, "v2": 45.2425}, close.mean(start=-80, keys=["v1", "v2"]))

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

    def test_apply(self):
        r = [x for x in range(20) if x % 2 == 0]

        close = self.create_series_by_list(r)
        f = lambda x : x**2
        fvec = np.vectorize(f)
        result = close.apply(keys="v1", func=fvec, start=None, end=None )

        target = [x**2 for x in range(20) if x % 2 == 0]

        try:
            np.testing.assert_almost_equal(target, result, 9)
        except AssertionError as e:
            self.fail(e.message)

        close = self.create_random_walk_series()
        import talib
        # talib.EMA is already supporting vectorized operation
        result = close.apply(keys="v1", func=talib.EMA, start=None, end=None, timeperiod=40)
        target = talib.EMA(np.array(close.get_series('v1')), timeperiod=40)

        result[np.isnan(result)] = 0
        target[np.isnan(target)] = 0

        deviation = np.sum((result - target)**2)
        self.assertTrue(deviation< 1e-6)

        try:
            np.testing.assert_almost_equal(target, result, 5)
        except AssertionError as e:
            self.fail(e.message)

