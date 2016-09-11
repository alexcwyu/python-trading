import datetime
import math
#from datetime import datetime
from unittest import TestCase

import numpy as np
import talib

from algotrader.technical.talib_wrapper import SMA
from algotrader.utils.time_series import DataSeries

from algotrader.config.app import ApplicationConfig
from algotrader.trading.context import ApplicationContext


class TALibSMATest(TestCase):
    def setUp(self):
        self.app_config = ApplicationConfig(None, None, None, None, None, None, None)
        self.app_context = ApplicationContext(app_config=self.app_config)



    def test_name(self):
        bar = self.app_context.inst_data_mgr.get_series("bar")
        bar.start(self.app_context)
        sma = SMA(bar, input_key='close', length=3)
        sma.start(self.app_context)

        self.assertEquals("SMA('bar',close,3)", sma.name)

        sma2 = SMA(sma, input_key='value', length=10)
        self.assertEquals("SMA(SMA('bar',close,3),value,10)", sma2.name)

    def test_empty_at_initialize(self):
        close = self.app_context.inst_data_mgr.get_series("bar")
        close.start(self.app_context)

        sma = SMA(close, 'close', 3)
        sma.start(self.app_context)

        self.assertEquals(0, len(sma.get_data()))

    def test_nan_before_size(self):
        bar = self.app_context.inst_data_mgr.get_series("bar")
        bar.start(self.app_context)

        sma = SMA(bar, 'close', 3)
        sma.start(self.app_context)

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)
        t3 = t2 + datetime.timedelta(0, 3)

        bar.add({"timestamp": t1, "close": 2.0, "open": 0})
        self.assertEquals([{"timestamp": t1, 'value': np.nan}],
                          sma.get_data())

        bar.add({"timestamp": t2, "close": 2.4, "open": 1.4})
        self.assertEquals([{"timestamp": t1, 'value': np.nan},
                           {"timestamp": t2, 'value': np.nan}],
                          sma.get_data())

        bar.add({"timestamp": t3, "close": 2.8, "open": 1.8})
        self.assertEquals([{"timestamp": t1, 'value': np.nan},
                           {"timestamp": t2, 'value': np.nan},
                           {"timestamp": t3, 'value': 2.4}],
                          sma.get_data())

    def test_moving_average_calculation(self):
        bar = self.app_context.inst_data_mgr.get_series("bar")
        bar.start(self.app_context)

        sma = SMA(bar, input_key='close', length=3)
        sma.start(self.app_context)

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)
        t3 = t2 + datetime.timedelta(0, 3)
        t4 = t3 + datetime.timedelta(0, 3)
        t5 = t4 + datetime.timedelta(0, 3)

        bar.add({"timestamp": t1, "close": 2.0, "open": 0})
        self.assertTrue(math.isnan(sma.now('value')))

        bar.add({"timestamp": t2, "close": 2.4, "open": 1.4})
        self.assertTrue(math.isnan(sma.now('value')))

        bar.add({"timestamp": t3, "close": 2.8, "open": 1.8})
        self.assertEquals(2.4, sma.now('value'))

        bar.add({"timestamp": t4, "close": 3.2, "open": 2.2})
        # self.assertEquals(2.8, sma.now('value'))
        self.assertAlmostEqual(2.8, sma.now('value'), places=3)

        bar.add({"timestamp": t5, "close": 3.6, "open": 2.6})
        self.assertAlmostEqual(3.2, sma.now('value'), places=3)
        # self.assertEquals(3.2, sma.now('value'))

        self.assertTrue(math.isnan(sma.get_by_idx(0, 'value')))
        self.assertTrue(math.isnan(sma.get_by_idx(1, 'value')))
        self.assertAlmostEqual(2.4, sma.get_by_idx(2, 'value'), places=3)
        self.assertAlmostEquals(2.8, sma.get_by_idx(3, 'value'), places=3)
        self.assertAlmostEquals(3.2, sma.get_by_idx(4, 'value'), places=3)

        self.assertTrue(math.isnan(sma.get_by_time(t1, 'value')))
        self.assertTrue(math.isnan(sma.get_by_time(t2, 'value')))
        self.assertAlmostEquals(2.4, sma.get_by_time(t3, 'value'), places=3)
        self.assertAlmostEquals(2.8, sma.get_by_time(t4, 'value'), places=3)
        self.assertAlmostEquals(3.2, sma.get_by_time(t5, 'value'), places=3)

    @staticmethod
    def create_series_by_list(valuelist):
        close = DataSeries("close")

        t = datetime.datetime(2000, 1, 1, 11, 34, 59)

        for value in valuelist:
            close.add({"timestamp": t, "v1": value})
            t = t + datetime.timedelta(0, 3)
        return close

    def test_compare_against_oneoff_calculation(self):
        rw = np.cumsum(np.random.normal(0, 2, 1000)) + 100
        close = DataSeries("close")
        close.start(self.app_context)

        t = datetime.datetime.now()
        sma = SMA(close, input_key='close', length=50)
        sma.start(self.app_context)

        result = []

        for x in rw:
            close.add({"timestamp": t, "close": x})
            result.append(sma.now('value'))
            t = t + datetime.timedelta(0, 3)

        result = np.array(result)

        # either apply or direct call is equivalent
        target = close.apply('close', start=None, end=None, func=talib.SMA, timeperiod=50)
        # target = talib.SMA(np.array(close.get_series('close')), timeperiod=50)

        result[np.isnan(result)] = 0
        target[np.isnan(target)] = 0

        try:
            np.testing.assert_almost_equal(target, result, 5)
        except AssertionError as e:
            self.fail(e.message)
