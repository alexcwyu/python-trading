from unittest import TestCase
import datetime
from datetime import timedelta
import numpy as np
import raccoon as rc
import pandas as pd
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from tests import test_override
from algotrader.trading.data_frame import Series, DataFrame


from algotrader import Startable, Context
from algotrader.model.model_factory import ModelFactory
from algotrader.model.time_series_pb2 import *
from algotrader.utils.date import *
import algotrader.model.time_series2_pb2 as proto
from algotrader.utils.proto_series_helper import get_proto_series_data, set_proto_series_data, to_np_type, from_np_type

from tests.test_series import SeriesTest

class DataFrameTest(TestCase):

    stg_override = {
        "Strategy": {
            "down2%": {
                "qty": 1000
            }
        }
    }

    def create_app_context(self, conf):
        return ApplicationContext(config=Config(
            load_from_yaml("../config/unittest.yaml"),
            load_from_yaml("../config/down2%.yaml"),
            test_override,
            {
                "Application": {
                    "ceateAtStart": True,
                    "deleteDBAtStop": False,
                    "persistenceMode": "RealTime"
            }
        },
        conf
    ))

    def __create_rc_dataframe(self):
        rc_df = rc.DataFrame({"a": [1.2, 2.3, 3.4],
                           "b": [1.6, 3.3, 6.6],
                           "c": [2.4, 6.3, -2.7]})

        return rc_df

    @staticmethod
    def create_df_by_rc_df():
        rc_df = rc.DataFrame({"a": [1.2, 2.3, 3.4],
                              "b": [1.6, 3.3, 6.6],
                              "c": [2.4, 6.3, -2.7]})
        return DataFrame.from_rc_dataframe(rc_df=rc_df, df_id="test_from_rc_df", provider_id="test")


    @staticmethod
    def create_df_backed_by_series_dict():
        open_data = [100., 101., 102.]
        close_data = [101., 103., 101.]
        d1 = datetime.datetime(2010, 6, 6, 9, 30, 0)
        proto_open = SeriesTest.create_proto_series(d1, open_data, 3, "open")
        proto_close = SeriesTest.create_proto_series(d1, close_data, 3, "close")

        op_sz = Series.from_proto_series(proto_open)
        cl_sz= Series.from_proto_series(proto_close)
        series_dict = {"open": op_sz, "close": cl_sz}

        return DataFrame.from_series_dict(series_dict=series_dict)


    def test_ctor_from_series_dict(self):
        open_data = [100., 101., 102.]
        close_data = [101., 103., 101.]
        d1 = datetime.datetime(2010, 6, 6, 9, 30, 0)
        proto_open = SeriesTest.create_proto_series(d1, open_data, 3, "open")
        proto_close = SeriesTest.create_proto_series(d1, close_data, 3, "close")

        op_sz = Series.from_proto_series(proto_open)
        cl_sz= Series.from_proto_series(proto_close)
        series_dict = {"open": op_sz, "close": cl_sz}

        df = DataFrame.from_series_dict(series_dict=series_dict)

        self.assertListEqual(['close', 'open'], df.columns)
        self.assertListEqual(open_data, df['open'].data[0])
        self.assertListEqual(close_data, df['close'].data[0])
        # rc_df = df.rc_df
        # rc_df.show()

    def test_append(self):
        # this dataframe does not have series_dict yet
        df = DataFrame(df_id="id", provider_id="p", inst_id="i", parent_df_id="pid", columns=['close', 'high'])

        d1 = datetime.datetime(2010, 6, 6, 9, 30, 0)
        d2 = d1 + timedelta(seconds=1)

        ts1 = datetime_to_unixtimemillis(d1)
        ts2 = datetime_to_unixtimemillis(d2)
        df.append_row(ts1, {"close" : 100.0})
        df.append_row(ts2, {"high" : 110.0})

        #df2 has series_dict
        df2 = DataFrameTest.create_df_backed_by_series_dict()
        t3 = unixtimemillis_to_datetime(df2.index[-1]) + timedelta(seconds=1)
        df2.append_row(t3, {"open" : 107, "close": 109})



    def test_rc_df_to_df(self):
        rc_df = self.__create_rc_dataframe()
        df = DataFrame.from_rc_dataframe(rc_df, "test_df", "test_source")
        series_dict = df.to_series_dict()

        self.assertTrue('a' in series_dict.keys())
        self.assertTrue('b' in series_dict.keys())
        self.assertTrue('c' in series_dict.keys())

        self.assertEqual("a", series_dict['a'].col_id)
        self.assertEqual("b", series_dict['b'].col_id)
        self.assertEqual("c", series_dict['c'].col_id)
        series_a = series_dict['a']
        self.assertEqual("test_df", series_a.df_id)
        self.assertEqual("test_df.test_source.a", series_a.series_id)
        self.assertEqual("test_source", series_a.provider_id)

        series_b = series_dict['b']
        series_c = series_dict['c']
        self.assertListEqual(list(series_a.data), [1.2, 2.3, 3.4])
        self.assertListEqual(list(series_b.data), [1.6, 3.3, 6.6])
        self.assertListEqual(list(series_c.data), [2.4, 6.3, -2.7])


    def test_to_series_dict(self):
        df = DataFrameTest.create_df_by_rc_df()
        series_dict = df.to_series_dict()


    # def test_sync_series(self):
    #     app_context = self.create_app_context(conf={
    #         "Application": {
    #             "createDBAtStart": True,
    #             "deleteDBAtStop": False,
    #             "persistenceMode": "RealTime"
    #         }
    #     })
    #     app_context.start()
    #
    #     series0 = app_context.inst_data_mgr.get_series("series0")
    #     series1 = app_context.inst_data_mgr.get_series("series1")
    #     series2 = app_context.inst_data_mgr.get_series("series2")
    #
    #     series0.start(app_context)
    #     series1.start(app_context)
    #     series2.start(app_context)
    #
    #     df = DataFrame([series0, series1, series2])
    #     df.start(app_context)
    #
    #     series0.add(0, 100)
    #     series1.add(0, 50)
    #     series2.add(0, 80)








    def __np_assert_almost_equal(self, target, output, precision=10):
        try:
            np.testing.assert_almost_equal(target, output, precision)
        except AssertionError as e:
            self.fail(e.message)

    #
    #
    # def __create_series(self):
    #     close = DataSeries(time_series=TimeSeries())
    #     t = 0
    #     for idx, value in enumerate(self.values):
    #         close.add(data={"timestamp": t, "v1": value, "v2": value})
    #         t = t + 3
    #
    #     return close
    #
    # @staticmethod
    # def create_random_walk_series():
    #     close = DataSeries(time_series=TimeSeries())
    #
    #     t1 = 1
    #     t = t1
    #     w = np.random.normal(0, 1, 1000)
    #     xs = 100 + np.cumsum(w)
    #
    #     for value in xs:
    #         close.add(data={"timestamp": t, "v1": value, "v2": value})
    #         t = t + 3
    #     return close
    #
    # @staticmethod
    # def create_series_by_list(valuelist):
    #     close = DataSeries(time_series=TimeSeries())
    #
    #     t = 0
    #
    #     for value in valuelist:
    #         close.add(data={"timestamp": t, "v1": value})
    #         t = t + 3
    #     return close
    #
    # def test_init_w_data(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test",
    #                                                   keys=["v1"])
    #     DataSeriesTest.factory.add_time_series_item(ts, 0, {"v1": 1})
    #     DataSeriesTest.factory.add_time_series_item(ts, 1, {"v1": 2})
    #     series = DataSeries(time_series=ts)
    #
    #     self.assertEqual(2, series.size())
    #
    #     result = series.get_data()
    #
    #     self.assertEqual(2, len(result))
    #     self.assertEqual(1, result[0]["v1"])
    #     self.assertEqual(2, result[1]["v1"])
    #
    # def test_init_w_keys(self):
    #
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test",
    #                                                   keys=["v1"])
    #
    #     series = DataSeries(time_series=ts)
    #
    #     series.add(data={"timestamp": 0, "v1": 1, "v2": 1})
    #
    #     result = series.get_data()
    #
    #     self.assertEqual(1, len(result))
    #     self.assertTrue("v1" in result[0])
    #     self.assertFalse("v2" in result[0])
    #
    # def test_add(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test")
    #
    #     series = DataSeries(time_series=ts)
    #
    #     self.assertTrue(len(series.get_data()) == 0)
    #
    #     series.add(data={"timestamp": 0, "v1": 1, "v2": 1})
    #     series.add(data={"timestamp": 1, "v1": 2, "v2": 2})
    #
    #     self.assertEqual([{"timestamp": 0, "v1": 1, "v2": 1},
    #                       {"timestamp": 1, "v1": 2, "v2": 2}], series.get_data())
    #
    #     series.add(data={"timestamp": 1, "v1": 3, "v2": 3})
    #
    #     self.assertEqual([{"timestamp": 0, "v1": 1, "v2": 1},
    #                       {"timestamp": 1, "v1": 3, "v2": 3}], series.get_data())
    #
    #     series.add(data={"timestamp": 2, "v1": 4, "v2": 4})
    #
    #     self.assertEqual([{"timestamp": 0, "v1": 1, "v2": 1},
    #                       {"timestamp": 1, "v1": 3, "v2": 3},
    #                       {"timestamp": 2, "v1": 4, "v2": 4}], series.get_data())
    #
    # def test_current_time(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test")
    #
    #     series = DataSeries(time_series=ts)
    #
    #     self.assertEqual(0, series.current_time())
    #
    #     series.add(data={"timestamp": 0, "v1": 1, "v2": 1})
    #     self.assertEqual(0, series.current_time())
    #
    #     series.add(data={"timestamp": 1, "v1": 1, "v2": 1})
    #     self.assertEqual(1, series.current_time())
    #
    #     series.add(data={"timestamp": 2, "v1": 2, "v2": 2})
    #     self.assertEqual(2, series.current_time())
    #
    # def test_get_data_dict(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test")
    #
    #     series = DataSeries(time_series=ts)
    #
    #     series.add(data={"timestamp": 1, "v1": 1, "v2": 1})
    #     series.add(data={"timestamp": 2, "v1": 2, "v2": 2})
    #
    #     self.assertEqual({"timestamp": {1: 1, 2: 2},
    #                       "v1": {1: 1, 2: 2},
    #                       "v2": {1: 1, 2: 2}}, series.get_data_dict())
    #
    #     self.assertEqual({"v1": {1: 1, 2: 2}, "v2": {1: 1, 2: 2}},
    #                      series.get_data_dict(['v1', 'v2']))
    #     self.assertEqual({1: 1, 2: 2}, series.get_data_dict('v1'))
    #
    # def test_get_data(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test")
    #
    #     series = DataSeries(time_series=ts)
    #
    #     series.add(data={"timestamp": 1, "v1": 1, "v2": 1})
    #     series.add(data={"timestamp": 2, "v1": 2, "v2": 2})
    #
    #     self.assertEqual([{"timestamp": 1, "v1": 1, "v2": 1},
    #                       {"timestamp": 2, "v1": 2, "v2": 2}], series.get_data())
    #
    # def test_get_series(self):
    #
    #     close = self.__create_series()
    #
    #     t = 0
    #     time_idx = []
    #     for idx, value in enumerate(self.values):
    #         time_idx.append(t)
    #         t = t + 3
    #
    #     v1 = pd.Series(self.values, index=time_idx, name='v1')
    #     v2 = pd.Series(self.values, index=time_idx, name='v2')
    #
    #     self.assertTrue(v1.equals(close.get_series('v1')))
    #
    #     result = close.get_series(['v1', 'v2'])
    #     self.assertTrue(len(result) == 2)
    #     self.assertTrue(v1.equals(result['v1']))
    #     self.assertTrue(v2.equals(result['v2']))
    #
    # def test_get_data_frame(self):
    #     close = self.__create_series()
    #
    #     t = 0
    #     time_idx = []
    #     for idx, value in enumerate(self.values):
    #         time_idx.append(t)
    #         t = t + 3
    #
    #     v1 = pd.Series(self.values, index=time_idx, name='v1')
    #     v2 = pd.Series(self.values, index=time_idx, name='v2')
    #
    #     df1 = pd.DataFrame({'v1': v1})
    #     df2 = pd.DataFrame({'v1': v1, 'v2': v2})
    #
    #     self.assertTrue(df1.equals(close.get_data_frame('v1')))
    #     self.assertTrue(df2.equals(close.get_data_frame(['v1', 'v2'])))
    #
    # def test_size(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test")
    #
    #     series = DataSeries(time_series=ts)
    #     self.assertEqual(0, series.size())
    #
    #     series.add(data={"timestamp": 0, "v1": 1})
    #     self.assertEqual(1, series.size())
    #
    #     series.add(data={"timestamp": 1, "v1": 1})
    #     self.assertEqual(2, series.size())
    #
    # def test_now(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test")
    #
    #     series = DataSeries(time_series=ts)
    #     self.assertEqual(0.0, series.now())
    #
    #     series.add(data={"timestamp": 0, "v1": 1, "v2": 2})
    #     self.assertEqual({"timestamp": 0, "v1": 1, "v2": 2}, series.now())
    #
    #     series.add(data={"timestamp": 1, "v1": 1.2, "v2": 2.2})
    #     self.assertEqual({"timestamp": 1, "v1": 1.2, "v2": 2.2}, series.now())
    #
    #     series.add(data={"timestamp": 2, "v1": 1.3, "v2": 2.3})
    #     series.add(data={"timestamp": 3, "v1": 1.4, "v2": 2.4})
    #
    #     self.assertEqual({"timestamp": 3, "v1": 1.4, "v2": 2.4}, series.now())
    #     self.assertEqual(1.4, series.now(["v1"]))
    #     self.assertEqual({"v1": 1.4, "v2": 2.4}, series.now(["v1", "v2"]))
    #
    # def test_ago(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test")
    #
    #     series = DataSeries(time_series=ts)
    #     self.assertEqual(0.0, series.now())
    #
    #     series.add(data={"timestamp": 0, "v1": 1, "v2": 2})
    #     self.assertEqual({"timestamp": 0, "v1": 1, "v2": 2}, series.ago(0))
    #
    #     series.add(data={"timestamp": 1, "v1": 1.2, "v2": 2.2})
    #     self.assertEqual({"timestamp": 1, "v1": 1.2, "v2": 2.2}, series.ago(0))
    #     self.assertEqual({"timestamp": 0, "v1": 1, "v2": 2}, series.ago(1))
    #
    #     series.add(data={"timestamp": 2, "v1": 1.3, "v2": 2.3})
    #     self.assertEqual({"timestamp": 2, "v1": 1.3, "v2": 2.3}, series.ago(0))
    #     self.assertEqual({"timestamp": 1, "v1": 1.2, "v2": 2.2}, series.ago(1))
    #     self.assertEqual({"timestamp": 0, "v1": 1, "v2": 2}, series.ago(2))
    #
    #     series.add(data={"timestamp": 3, "v1": 1.4, "v2": 2.4})
    #     self.assertEqual({"timestamp": 3, "v1": 1.4, "v2": 2.4}, series.ago(0))
    #     self.assertEqual({"timestamp": 2, "v1": 1.3, "v2": 2.3}, series.ago(1))
    #     self.assertEqual({"timestamp": 1, "v1": 1.2, "v2": 2.2}, series.ago(2))
    #     self.assertEqual({"timestamp": 0, "v1": 1, "v2": 2}, series.ago(3))
    #
    #     self.assertEqual({"v1": 1.4, "v2": 2.4}, series.ago(0, ["v1", "v2"]))
    #     self.assertEqual(1.4, series.ago(0, "v1"))
    #     self.assertEqual(1.4, series.ago(0, ["v1"]))
    #
    # def test_get_by_idx(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test", keys=["timestamp", "v1", "v2"])
    #
    #     series = DataSeries(time_series=ts)
    #
    #     series.add(data={"timestamp": 0, "v1": 2})
    #     series.add(data={"timestamp": 1, "v1": 2.4})
    #     series.add(data={"timestamp": 1, "v2": 3.0})
    #
    #     # index and key
    #     self.assertEqual(2, series.get_by_idx(idx=0, keys="v1"))
    #     self.assertEqual(0.0, series.get_by_idx(idx=0, keys="v2"))
    #     self.assertEqual(2.4, series.get_by_idx(idx=1, keys="v1"))
    #     self.assertEqual(3.0, series.get_by_idx(idx=1, keys="v2"))
    #
    #     # index only
    #     self.assertEqual({"timestamp": 0, "v1": 2, "v2": 0.0}, series.get_by_idx(idx=0))
    #     self.assertEqual({"timestamp": 1, "v1": 2.4, "v2": 3.0}, series.get_by_idx(idx=1))
    #
    #     # test index slice
    #     series2 = self.create_series_by_list(range(100))
    #     sliced = series2.get_by_idx(keys='v1', idx=slice(-10, None, None))
    #     self.assertEqual(len(sliced), 10)
    #
    #     endPoint = series2.get_by_idx(keys='v1', idx=slice(-1, None, None))
    #     self.assertEqual(endPoint[0], 99)
    #
    # def test_get_by_time(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test", keys=["timestamp", "v1", "v2"])
    #
    #     series = DataSeries(time_series=ts)
    #
    #     # time and key
    #     series.add(data={"timestamp": 0, "v1": 2})
    #     series.add(data={"timestamp": 1, "v1": 2.4})
    #     series.add(data={"timestamp": 1, "v2": 3.0})
    #
    #     self.assertEqual(2, series.get_by_time(time=0, keys="v1"))
    #     self.assertEqual(0.0, series.get_by_time(time=0, keys="v2"))
    #     self.assertEqual(2.4, series.get_by_time(time=1, keys="v1"))
    #     self.assertEqual(3.0, series.get_by_time(time=1, keys="v2"))
    #     # time only
    #     self.assertEqual({"timestamp": 0, "v1": 2, "v2": 0.0}, series.get_by_time(time=0))
    #     self.assertEqual({"timestamp": 1, "v1": 2.4, "v2": 3.0}, series.get_by_time(time=1))
    #
    # def test_override_w_same_time(self):
    #     ts = DataSeriesTest.factory.build_time_series(series_id="test", keys=["timestamp", "v1", "v2", "v3"])
    #
    #     series = DataSeries(time_series=ts)
    #
    #     series.add(data={"timestamp": 1, "v1": 2, "v2": 3})
    #     self.assertEqual(1, series.size())
    #     self.assertEqual(2, series.get_by_idx(0, "v1"))
    #     self.assertEqual(2, series.get_by_time(1, "v1"))
    #     self.assertEqual(3, series.get_by_idx(0, "v2"))
    #     self.assertEqual(3, series.get_by_time(1, "v2"))
    #     self.assertEqual(0.0, series.get_by_idx(0, "v3"))
    #     self.assertEqual(0.0, series.get_by_time(1, "v3"))
    #
    #     series.add(data={"timestamp": 1, "v1": 2.4, "v2": 3.4, "v3": 1.1})
    #     self.assertEqual(1, series.size())
    #     self.assertEqual(2.4, series.get_by_idx(0, "v1"))
    #     self.assertEqual(2.4, series.get_by_time(1, "v1"))
    #     self.assertEqual(3.4, series.get_by_idx(0, "v2"))
    #     self.assertEqual(3.4, series.get_by_time(1, "v2"))
    #     self.assertEqual(1.1, series.get_by_idx(0, "v3"))
    #     self.assertEqual(1.1, series.get_by_time(1, "v3"))
    #
    #     series.add(data={"timestamp": 2, "v1": 2.6, "v2": 3.6})
    #     self.assertEqual(2, series.size())
    #     self.assertEqual(2.4, series.get_by_idx(0, "v1"))
    #     self.assertEqual(2.4, series.get_by_time(1, "v1"))
    #     self.assertEqual(3.4, series.get_by_idx(0, "v2"))
    #     self.assertEqual(3.4, series.get_by_time(1, "v2"))
    #     self.assertEqual(1.1, series.get_by_idx(0, "v3"))
    #     self.assertEqual(1.1, series.get_by_time(1, "v3"))
    #
    #     self.assertEqual(2.6, series.get_by_idx(1, "v1"))
    #     self.assertEqual(2.6, series.get_by_time(2, "v1"))
    #     self.assertEqual(3.6, series.get_by_idx(1, "v2"))
    #     self.assertEqual(3.6, series.get_by_time(2, "v2"))
    #     self.assertEqual(0.0, series.get_by_idx(1, "v3"))
    #     self.assertEqual(0.0, series.get_by_time(2, "v3"))
    #
    # def test_subscript(self):
    #     close = self.__create_series()
    #     self.assertEquals([np.nan, np.nan], close[0:2, "v1"])
    #     self.assertEquals({"v1": [np.nan, np.nan, 44.34, 44.09], "v2": [np.nan, np.nan, 44.34, 44.09]},
    #                       close[0:4, ["v1", "v2"]])
    #
    #     self.assertEquals([np.nan, np.nan, 44.34, 44.09], close[0:4, "v1"])
    #     self.assertEquals([np.nan, np.nan, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83], close[0:8, "v1"])
    #     self.assertEquals([45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.0], close[-8:, "v1"])
    #
    # def test_mean(self):
    #     close = self.__create_series()
    #     self.assertAlmostEqual(45.2425, close.mean(start=-80, keys="v1"))
    #     self.assertAlmostEqual({"v1": 45.2425, "v2": 45.2425}, close.mean(start=-80, keys=["v1", "v2"]))
    #
    #     self.assertAlmostEqual(45.2425, close.mean(keys="v1"))
    #     self.assertAlmostEqual(44.215, close.mean(start=0, end=4, keys="v1"))
    #     self.assertAlmostEqual(44.0475, close.mean(start=0, end=6, keys="v1"))
    #
    # def test_median(self):
    #     close = self.__create_series()
    #     self.assertAlmostEqual(45.515, close.median(keys="v1"))
    #     self.assertAlmostEqual(44.215, close.median(start=0, end=4, keys="v1"))
    #     self.assertAlmostEqual(44.12, close.median(start=0, end=6, keys="v1"))
    #
    # def test_max(self):
    #     close = self.__create_series()
    #     self.assertAlmostEqual(46.28, close.max(keys="v1"))
    #     self.assertAlmostEqual(44.34, close.max(start=0, end=4, keys="v1"))
    #     self.assertAlmostEqual(44.34, close.max(start=0, end=6, keys="v1"))
    #
    # def test_min(self):
    #     close = self.__create_series()
    #     self.assertAlmostEqual(43.61, close.min(keys="v1"))
    #     self.assertAlmostEqual(44.09, close.min(start=0, end=4, keys="v1"))
    #     self.assertAlmostEqual(43.61, close.min(start=0, end=6, keys="v1"))
    #
    # def test_std(self):
    #     close = self.__create_series()
    #     self.assertAlmostEqual(0.866584531364, close.std(keys="v1"))
    #     self.assertAlmostEqual(0.125, close.std(start=0, end=4, keys="v1"))
    #     self.assertAlmostEqual(0.268921456935, close.std(start=0, end=6, keys="v1"))
    #
    # def test_var(self):
    #     close = self.__create_series()
    #     self.assertAlmostEqual(0.75096875, close.var(keys="v1"))
    #     self.assertAlmostEqual(0.015625, close.var(start=0, end=4, keys="v1"))
    #     self.assertAlmostEqual(0.07231875, close.var(start=0, end=6, keys="v1"))
    #
    # def test_apply(self):
    #     r = [x for x in range(20) if x % 2 == 0]
    #
    #     close = self.create_series_by_list(r)
    #     f = lambda x: x ** 2
    #     fvec = np.vectorize(f)
    #     result = close.apply(keys="v1", func=fvec, start=None, end=None)
    #
    #     target = [x ** 2 for x in range(20) if x % 2 == 0]
    #
    #     try:
    #         np.testing.assert_almost_equal(target, result, 9)
    #     except AssertionError as e:
    #         self.fail(e.message)
    #
    #     close = self.create_random_walk_series()
    #     import talib
    #     # talib.EMA is already supporting vectorized operation
    #     result = close.apply(keys="v1", func=talib.EMA, start=None, end=None, timeperiod=40)
    #     target = talib.EMA(np.array(close.get_series('v1')), timeperiod=40)
    #
    #     result[np.isnan(result)] = 0
    #     target[np.isnan(target)] = 0
    #
    #     deviation = np.sum((result - target) ** 2)
    #     self.assertTrue(deviation < 1e-6)
    #
    #     try:
    #         np.testing.assert_almost_equal(target, result, 5)
    #     except AssertionError as e:
    #         self.fail(e.message)

