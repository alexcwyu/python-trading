from unittest import TestCase
import talib
import numpy as np
import raccoon as rc
import pandas as pd

from algotrader import Startable, Context
from algotrader.model.model_factory import ModelFactory
from algotrader.model.time_series_pb2 import *
from algotrader.trading.series import Series
from algotrader.trading.data_frame import DataFrame
from algotrader.technical.talib_wrapper import *

import algotrader.model.time_series2_pb2 as proto
from algotrader.model.time_series_pb2 import TimeSeriesUpdateEvent
from algotrader.utils.proto_series_helper import get_proto_series_data, set_proto_series_data, to_np_type, from_np_type
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from tests import test_override
import datetime
from datetime import timedelta
from algotrader.utils.date import *

class TALibWrapperTest(TestCase):

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

    def setUp(self):
        self.pd_df = pd.read_json('../data/tradedata/hsi_df.json')

    def test_atr(self):
        app_context = self.create_app_context(conf={
            "Application": {
                "createDBAtStart": True,
                "deleteDBAtStop": False,
                "persistenceMode": "RealTime"
            }
        })
        app_context.start()
        # print(self.pd_df.head())

        self.pd_df.rename(columns={'Last' : 'Close'}, inplace=True)
        df = DataFrame.from_pd_dataframe(self.pd_df, 'Bar.HSI', 'test', 'HSI')
        df.start(app_context)
        app_context.inst_data_mgr.add_frame(df)

        atr20f = atr20 * df

        atr20f.start(app_context)
        atr20f.evaluate()

        atr20_df = atr20f.to_pd_dataframe()

        target = talib.ATR(np.array(self.pd_df.High.values, dtype='f8'),
                           np.array(self.pd_df.Low.values, dtype='f8'),
                           np.array(self.pd_df.Close.values, dtype='f8'), 20)
        self.__np_assert_almost_equal(target, atr20_df['atr20'].values)



    def __np_assert_almost_equal(self, target, output, precision=10):
            try:
                np.testing.assert_almost_equal(target, output, precision)
            except AssertionError as e:
                self.fail(e.message)






# import datetime
# import math
# import numpy as np
# import talib
# from unittest import TestCase
#
# from algotrader.technical.talib_wrapper import SMA
# from algotrader.trading.context import ApplicationContext
# from algotrader.trading.data_series import DataSeries
# from algotrader.model.model_factory import ModelFactory
#
#
# class TALibSMATest(TestCase):
#     def setUp(self):
#         self.app_context = ApplicationContext()
#
#     def test_name(self):
#         bar = self.app_context.inst_data_mgr.get_series("bar")
#         bar.start(self.app_context)
#         sma = SMA(inputs=bar, input_keys='close', length=3)
#         sma.start(self.app_context)
#
#         self.assertEquals("SMA(bar[close],length=3)", sma.name)
#
#         sma2 = SMA(inputs=sma, input_keys='value', length=10)
#         self.assertEquals("SMA(SMA(bar[close],length=3)[value],length=10)", sma2.name)
#
#     def test_empty_at_initialize(self):
#         close = self.app_context.inst_data_mgr.get_series("bar")
#         close.start(self.app_context)
#
#         sma = SMA(inputs=close, input_keys='close', length=3)
#         sma.start(self.app_context)
#
#         self.assertEquals(0, len(sma.get_data()))
#
#     def test_nan_before_size(self):
#         bar = self.app_context.inst_data_mgr.get_series("bar")
#         bar.start(self.app_context)
#
#         sma = SMA(inputs=bar, input_keys='close', length=3)
#         sma.start(self.app_context)
#
#         t1 = 1
#         t2 = t1 + 3
#         t3 = t2 + 3
#
#         bar.add(timestamp=t1, data={"close": 2.0, "open": 0})
#         self.assertEquals([{'value': np.nan}],
#                           sma.get_data())
#
#         bar.add(timestamp=t2, data={"close": 2.4, "open": 1.4})
#         self.assertEquals([{'value': np.nan},
#                            {'value': np.nan}],
#                           sma.get_data())
#
#         bar.add(timestamp=t3, data={"close": 2.8, "open": 1.8})
#         self.assertEquals([{'value': np.nan},
#                            {'value': np.nan},
#                            {'value': 2.4}],
#                           sma.get_data())
#
#     def test_moving_average_calculation(self):
#         bar = self.app_context.inst_data_mgr.get_series("bar")
#         bar.start(self.app_context)
#
#         sma = SMA(inputs=bar, input_keys='close', length=3)
#         sma.start(self.app_context)
#
#         t1 = 1
#         t2 = t1 + 3
#         t3 = t2 + 3
#         t4 = t3 + 3
#         t5 = t4 + 3
#
#         bar.add(timestamp=t1, data={"close": 2.0, "open": 0})
#         self.assertTrue(math.isnan(sma.now('value')))
#
#         bar.add(timestamp=t2, data={"close": 2.4, "open": 1.4})
#         self.assertTrue(math.isnan(sma.now('value')))
#
#         bar.add(timestamp=t3, data={"close": 2.8, "open": 1.8})
#         self.assertEquals(2.4, sma.now('value'))
#
#         bar.add(timestamp=t4, data={"close": 3.2, "open": 2.2})
#         # self.assertEquals(2.8, sma.now('value'))
#         self.assertAlmostEqual(2.8, sma.now('value'), places=3)
#
#         bar.add(timestamp=t5, data={"close": 3.6, "open": 2.6})
#         self.assertAlmostEqual(3.2, sma.now('value'), places=3)
#         # self.assertEquals(3.2, sma.now('value'))
#
#         self.assertTrue(math.isnan(sma.get_by_idx(0, 'value')))
#         self.assertTrue(math.isnan(sma.get_by_idx(1, 'value')))
#         self.assertAlmostEqual(2.4, sma.get_by_idx(2, 'value'), places=3)
#         self.assertAlmostEquals(2.8, sma.get_by_idx(3, 'value'), places=3)
#         self.assertAlmostEquals(3.2, sma.get_by_idx(4, 'value'), places=3)
#
#         self.assertTrue(math.isnan(sma.get_by_time(t1, 'value')))
#         self.assertTrue(math.isnan(sma.get_by_time(t2, 'value')))
#         self.assertAlmostEquals(2.4, sma.get_by_time(t3, 'value'), places=3)
#         self.assertAlmostEquals(2.8, sma.get_by_time(t4, 'value'), places=3)
#         self.assertAlmostEquals(3.2, sma.get_by_time(t5, 'value'), places=3)
#
#     @staticmethod
#     def create_series_by_list(valuelist):
#         close = DataSeries(time_series=ModelFactory.build_time_series(series_id="close"))
#
#         t = 1
#
#         for value in valuelist:
#             close.add(timestamp=t, data={"v1": value})
#             t = t + 3
#         return close
#
#     def test_compare_against_oneoff_calculation(self):
#         rw = np.cumsum(np.random.normal(0, 2, 1000)) + 100
#         close = DataSeries(time_series=ModelFactory.build_time_series(series_id="close"))
#         close.start(self.app_context)
#
#         t = 1
#         sma = SMA(inputs=close, input_keys='close', length=50)
#         sma.start(self.app_context)
#
#         result = []
#
#         for x in rw:
#             close.add(timestamp=t, data={"close": x})
#             result.append(sma.now('value'))
#             t = t + 3
#
#         result = np.array(result)
#
#         # either apply or direct call is equivalent
#         target = close.apply('close', start=None, end=None, func=talib.SMA, timeperiod=50)
#         # target = talib.SMA(np.array(close.get_series('close')), timeperiod=50)
#
#         result[np.isnan(result)] = 0
#         target[np.isnan(target)] = 0
#
#         try:
#             np.testing.assert_almost_equal(target, result, 5)
#         except AssertionError as e:
#             self.fail(e.message)
