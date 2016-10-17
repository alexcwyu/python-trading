import datetime
import math
from unittest import TestCase

import numpy as np

from algotrader.config.app import ApplicationConfig
from algotrader.technical.ma import SMA
from algotrader.trading.context import ApplicationContext


class MovingAverageTest(TestCase):
    def setUp(self):
        self.app_context = ApplicationContext()

    def test_name(self):
        bar = self.app_context.inst_data_mgr.get_series("bar")
        sma = SMA(bar, input_key='close', length=3)
        self.assertEquals("SMA('bar',close,3)", sma.name)

        sma2 = SMA(sma, input_key='value', length=10)
        self.assertEquals("SMA(SMA('bar',close,3),value,10)", sma2.name)

    def test_empty_at_initialize(self):
        close = self.app_context.inst_data_mgr.get_series("bar")
        sma = SMA(close, 'close', 3)
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
        self.assertEquals([{"name": "'SMA('bar',close,3)'",
                            "timestamp": t1, 'value': np.nan}],
                          sma.get_data())

        bar.add({"timestamp": t2, "close": 2.4, "open": 1.4})
        self.assertEquals([{"name": "'SMA('bar',close,3)'", "timestamp": t1, 'value': np.nan},
                           {"name": "'SMA('bar',close,3)'", "timestamp": t2, 'value': np.nan}],
                          sma.get_data())

        bar.add({"timestamp": t3, "close": 2.8, "open": 1.8})
        self.assertEquals([{"name": "'SMA('bar',close,3)'", "timestamp": t1, 'value': np.nan},
                           {"name": "'SMA('bar',close,3)'", "timestamp": t2, 'value': np.nan},
                           {"name": "'SMA('bar',close,3)'", "timestamp": t3, 'value': 2.4}],
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
        self.assertEquals(2.8, sma.now('value'))

        bar.add({"timestamp": t5, "close": 3.6, "open": 2.6})
        self.assertEquals(3.2, sma.now('value'))

        self.assertTrue(math.isnan(sma.get_by_idx(0, 'value')))
        self.assertTrue(math.isnan(sma.get_by_idx(1, 'value')))
        self.assertEquals(2.4, sma.get_by_idx(2, 'value'))
        self.assertEquals(2.8, sma.get_by_idx(3, 'value'))
        self.assertEquals(3.2, sma.get_by_idx(4, 'value'))

        self.assertTrue(math.isnan(sma.get_by_time(t1, 'value')))
        self.assertTrue(math.isnan(sma.get_by_time(t2, 'value')))
        self.assertEquals(2.4, sma.get_by_time(t3, 'value'))
        self.assertEquals(2.8, sma.get_by_time(t4, 'value'))
        self.assertEquals(3.2, sma.get_by_time(t5, 'value'))

