from unittest import TestCase
import numpy as np
import raccoon as rc
import pandas as pd

from algotrader import Startable, Context
from algotrader.model.model_factory import ModelFactory
from algotrader.model.time_series_pb2 import *
from algotrader.trading.series import Series

import algotrader.model.time_series2_pb2 as proto
from algotrader.model.time_series_pb2 import TimeSeriesUpdateEvent
from algotrader.utils.proto_series_helper import get_proto_series_data, set_proto_series_data, to_np_type, from_np_type
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from tests import test_override
import datetime
from datetime import timedelta
from algotrader.utils.date import *


class SeriesTest(TestCase):
    value10 = 20000 + np.cumsum(np.random.normal(0,100,10))
    value5 = 20000 + np.cumsum(np.random.normal(0,100,5))

    factory = ModelFactory()

    def __create_empty_proto_series(self):
        df_id = "Bar.Daily"
        inst_id ="HSI@SEHK"

        proto_series = proto.Series()
        proto_series.series_id = "Bar.Daily.close-HSI@SEHK"
        proto_series.df_id = df_id
        proto_series.col_id = "close"
        proto_series.inst_id = inst_id
        proto_series.provider_id= "Dummy Provider"
        proto_series.dtype = proto.DTDouble
        return proto_series

    @staticmethod
    def create_proto_series(start_date, values, n, col_id):
        df_id = "Bar.Daily"
        inst_id ="HSI@SEHK"

        dates = [start_date + timedelta(seconds=i) for i in range(n)]
        ts = [datetime_to_unixtimemillis(d) for d in dates]

        proto_series1 = proto.Series()
        proto_series1.series_id = "Bar.Daily.close-HSI@SEHK"
        proto_series1.df_id = df_id
        proto_series1.col_id = col_id
        proto_series1.inst_id = inst_id
        proto_series1.provider_id= "Dummy Provider"
        proto_series1.dtype = proto.DTDouble
        proto_series1.index.extend(ts)
        proto_series1.double_data.extend(values)
        return proto_series1


    def __create_proto_series1(self):
        df_id = "Bar.Daily"
        inst_id ="HSI@SEHK"

        proto_series1 = proto.Series()
        proto_series1.series_id = "Bar.Daily.close-HSI@SEHK"
        proto_series1.df_id = df_id
        proto_series1.col_id = "close"
        proto_series1.inst_id = inst_id
        proto_series1.provider_id= "Dummy Provider"
        proto_series1.dtype = proto.DTDouble
        proto_series1.index.extend(list(range(1499787464853, 1499887464853, 20000000)))
        proto_series1.double_data.extend(SeriesTest.value5)
        return proto_series1

    def __create_proto_series2(self):
        df_id = "Bar.Daily"
        inst_id ="HSI@SEHK"
        proto_series2 = proto.Series()
        proto_series2.series_id = "Bar.Daily.open-HSI@SEHK"
        proto_series2.df_id = df_id
        proto_series2.col_id = "open"
        proto_series2.inst_id = inst_id
        proto_series2.provider_id= "Dummy Provider2"
        proto_series2.dtype = proto.DTDouble
        proto_series2.index.extend(list(range(1499787464853, 1499887464853, 10000000)))
        proto_series2.double_data.extend(SeriesTest.value10)
        return proto_series2


    def __create_empty_series(self):
        df_id = "Bar.Daily"
        inst_id ="HSI@SEHK"
        series = Series()


    def __create_pd_series(self):
        df = pd.DataFrame({"a" : [60*i for i in range(20)], "x" : np.random.normal(0,1,20).tolist()})
        df['timestamp'] = pd.to_datetime(df['a'], unit='s', origin=pd.Timestamp('2010-01-01'))
        df = df.set_index('timestamp')
        return df['x']


    def create_app_context(self, conf):
        return ApplicationContext(config=Config(
            load_from_yaml("../config/backtest.yaml"),
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

    def test_empty_series_ctor(self):
        series = Series()
        self.assertEqual('', series.inst_id)
        self.assertEqual('', series.df_id)
        self.assertEqual('', series.col_id)
        self.assertEqual(np.float64, series.dtype)


    # def test_ctor_series(self):
    #
    #     try:
    #
    #         series = Series(series_id="Bar.Daily.open-HSI@HKFE", df_id="Bar.Daily", col_id="open", inst_id="HSI@HKFE")
    #         series.add(1499787464853, 20123)
    #         series.add(1499788464853, 20277)
    #         series.add(1499798464853, 20199)
    #         proto_s = series.to_proto_series()
    #     except Exception:
    #         self.fail("series ctor raised ExceptionType unexpectedly!")
    #

    def test_ctor_from_to_proto(self):
        proto_series = self.__create_proto_series1()
        series = Series.from_proto_series(proto_series)

        self.assertEqual("Bar.Daily.close-HSI@SEHK", series.series_id)
        self.assertEqual("Bar.Daily", series.df_id)
        self.assertEqual("close", series.col_id)
        self.assertEqual("HSI@SEHK", series.inst_id)
        self.assertEqual(to_np_type(proto.DTDouble), series.dtype)

        res_data = np.array(series.data)
        self.__np_assert_almost_equal(SeriesTest.value5, res_data)

        proto_series_out = series.to_proto_series()
        self.assertListEqual(list(proto_series_out.index), list(proto_series.index))
        self.assertListEqual(get_proto_series_data(proto_series_out), get_proto_series_data(proto_series))
        self.assertEqual(proto.DTDouble, proto_series_out.dtype)

    def test_ctor_from_to_pandas(self):
        pd_series = self.__create_pd_series()
        orig_data = pd_series.values
        series = Series.from_pd_series(pd_series, "test_series", "test_df", "test_col",
                                       "test_inst", "test_source")

        res_data = np.array(series.data)
        self.__np_assert_almost_equal(orig_data, res_data)

        pd_series_out = series.to_pd_series()
        self.assertTrue(pd_series.equals(pd_series_out))

    def test_pd_rc_proto(self):
        pd_series = self.__create_pd_series()

        series = Series.from_pd_series(pd_series, "test_series", "test_df", "test_col", "test_inst", "test_source")
        proto_series = series.to_proto_series()

        series_r = Series.from_proto_series(proto_series)
        pd_series_r = series_r.to_pd_series()

        self.assertTrue(pd_series.equals(pd_series_r))

    def test_from_list(self):
        data_list = np.random.normal(0, 1, 20)

        series = Series.from_list(data_list.tolist(), np.float64,
                                  index=list(range(20)),
                                  series_id="test_series",
                                  df_id="test", col_id="col",
                                  inst_id="test_inst",
                                  provider_id="test_source")

        out_arr = series.to_np_array()
        self.__np_assert_almost_equal(data_list, out_arr)

        # proto_series = series.to_proto_series()

    def test_add(self):
        proto_series = self.__create_empty_proto_series()
        series = Series.from_proto_series(proto_series)

        t0 = datetime.datetime.now()
        ts0 = datetime_to_unixtimemillis(t0)

        series.add(ts0, value=3.14)

        t1 = t0 + datetime.timedelta(seconds=20)
        ts1 = datetime_to_unixtimemillis(t1)

        series.add(ts1, value=2.87)

        pd_series = series.to_pd_series()

        self.__np_assert_almost_equal(np.array([3.14, 2.87]), pd_series.values)





    # def test_bind(self):
    #     import numpy as np
    #     proto_series = self.__create_proto_series1()
    #     series = Series.from_proto_series(proto_series)
    #
    #     ds = series.bind(np.sqrt)
    #
    #     self.assertEqual("Bar.Daily.close-HSI@SEHK", series.series_id)
    #     self.assertEqual("Bar.Daily", series.df_id)
    #     self.assertEqual("close", series.col_id)
    #     self.assertEqual("HSI@SEHK", series.inst_id)
    #     self.assertEqual(to_np_type(proto.DTDouble), series.dtype)
    #
    #     ds2 = series >> np.sqrt



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
