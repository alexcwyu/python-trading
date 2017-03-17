import math

import talib
from datetime import datetime
from unittest import TestCase
import numpy as np
import datetime
from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
from algotrader.technical.pipeline.pairwise import Plus, Minus, Times, Divides, Greater, PairCorrelation
from algotrader.technical.talib_wrapper import SMA
from algotrader.trading.data_series import DataSeries
from algotrader.config.app import ApplicationConfig
from algotrader.trading.context import ApplicationContext


class PairwiseTest(TestCase):
    def setUp(self):
        self.app_context = ApplicationContext()

    def test_name(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")

        bar0.start(self.app_context)
        bar1.start(self.app_context)

        bar0_plus_bar1 = Plus(bar0, bar1, input_key='close')
        bar0_plus_bar1.start(self.app_context)

        self.assertEquals("Plus('bar0','bar1',close)",
                          bar0_plus_bar1.name)

        spread = Minus(bar0, bar1, input_key='close')
        spread.start(self.app_context)

        self.assertEquals("Minus('bar0','bar1',close)",
                          spread.name)

    def test_empty_at_initialize(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")

        bar0.start(self.app_context)
        bar1.start(self.app_context)

        bar0_plus_bar1 = Plus(bar0, bar1, input_key='close')
        bar0_plus_bar1.start(self.app_context)

        self.assertEquals(0, len(bar0_plus_bar1.get_data()))

    def test_shape(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")

        bar0.start(self.app_context)
        bar1.start(self.app_context)

        bar0_plus_bar1 = Plus(bar0, bar1, input_key='close')
        bar0_plus_bar1.start(self.app_context)

        try:
            np.testing.assert_almost_equal(np.array([1, 1]), bar0_plus_bar1.shape(), 5)
        except AssertionError as e:
            self.fail(e.message)


    # def test_nan_before_size(self):
    def test_with_single_bar_multi_time(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")

        bar0.start(self.app_context)
        bar1.start(self.app_context)

        plus = Plus(bar0, bar1, input_key='close')
        minus = Minus(bar0, bar1, input_key='close')
        times = Times(bar0, bar1, input_key='close')
        divides = Divides(bar0, bar1, input_key='close')
        pcorr = PairCorrelation(bar0, bar1, length=4, input_key='close')

        plus.start(self.app_context)
        minus.start(self.app_context)
        times.start(self.app_context)
        divides.start(self.app_context)
        pcorr.start(self.app_context)

        now = datetime.datetime.now()
        x = np.array([80.0, 102.0, 101.0, 99.0])
        y = np.array([95.0, 98.0, 105.2, 103.3])
        ts = [now + datetime.timedelta(0, i*3) for i in range(4)]
        x_p_y = x + y
        x_m_y = x - y
        x_t_y = x * y
        x_d_y = x / y

        bar0.add({"timestamp": ts[0], "close": x[0], "open": 0})
        bar1.add({"timestamp": ts[0], "close": y[0], "open": 0})

        self.assertEqual(plus.now('value'), 175.0)
        self.assertEqual(minus.now('value'), -15.0)
        self.assertEqual(times.now('value'), 7600.0)
        self.assertEqual(divides.now('value'), 80.0/95.0)

        bar0.add({"timestamp": ts[1], "close": x[1], "open": 0})
        bar1.add({"timestamp": ts[1], "close": y[1], "open": 0})

        self.assertEqual(plus.now('value'), 200.0)
        self.assertEqual(minus.now('value'), 4.0)
        self.assertEqual(times.now('value'), 102.0*98.0)
        self.assertEqual(divides.now('value'), 102.0/98.0)

        bar0.add({"timestamp": ts[2], "close": x[2], "open": 0})
        bar1.add({"timestamp": ts[2], "close": y[2], "open": 0})

        bar0.add({"timestamp": ts[3], "close": x[3], "open": 0})
        bar1.add({"timestamp": ts[3], "close": y[3], "open": 0})

        self.assertEqual(pcorr.now('value'), np.corrcoef(x, y)[0, 1])
