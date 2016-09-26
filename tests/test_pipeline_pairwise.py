import math

import talib
from datetime import datetime
from unittest import TestCase
import numpy as np
import datetime
from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
from algotrader.technical.pipeline.pairwise import Plus, Minus, Times, Divides, Greater
from algotrader.technical.talib_wrapper import SMA
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.utils.time_series import DataSeries


class PairwiseTest(TestCase):
    def test_name(self):
        inst_data_mgr.clear()
        bar0 = inst_data_mgr.get_series("bar0")
        bar1 = inst_data_mgr.get_series("bar1")

        bar0_plus_bar1 = Plus(bar0, bar1, input_key='close')

        self.assertEquals("Plus('bar0','bar1',close)",
                          bar0_plus_bar1.name)

        spread = Minus(bar0, bar1, input_key='close')
        self.assertEquals("Minus('bar0','bar1',close)",
                          spread.name)

    def test_empty_at_initialize(self):

        inst_data_mgr.clear()
        bar0 = inst_data_mgr.get_series("bar0")
        bar1 = inst_data_mgr.get_series("bar1")

        bar0_plus_bar1 = Plus(bar0, bar1, input_key='close')
        self.assertEquals(0, len(bar0_plus_bar1.get_data()))

    def test_shape(self):
        inst_data_mgr.clear()
        bar0 = inst_data_mgr.get_series("bar0")
        bar1 = inst_data_mgr.get_series("bar1")

        bar0_plus_bar1 = Plus(bar0, bar1, input_key='close')

        try:
            np.testing.assert_almost_equal(np.array([1, 1]), bar0_plus_bar1.shape(), 5)
        except AssertionError as e:
            self.fail(e.message)


    # def test_nan_before_size(self):
    def test_with_single_bar_multi_time(self):
        inst_data_mgr.clear()
        bar0 = inst_data_mgr.get_series("bar0")
        bar1 = inst_data_mgr.get_series("bar1")

        plus = Plus(bar0, bar1, input_key='close')
        minus = Minus(bar0, bar1, input_key='close')
        times = Times(bar0, bar1, input_key='close')
        divides = Divides(bar0, bar1, input_key='close')

        t1 = datetime.datetime.now()
        bar0.add({"timestamp": t1, "close": 80.0, "open": 0})
        bar1.add({"timestamp": t1, "close": 95.0, "open": 0})

        self.assertEqual(plus.now('value'), 175.0)
        self.assertEqual(minus.now('value'), -15.0)
        self.assertEqual(times.now('value'), 7600.0)
        self.assertEqual(divides.now('value'), 80.0/95.0)

        t2 = t1 + datetime.timedelta(0, 3)

        bar0.add({"timestamp": t2, "close": 102.0, "open": 0})
        bar1.add({"timestamp": t2, "close": 98.0, "open": 0})

        self.assertEqual(plus.now('value'), 200.0)
        self.assertEqual(minus.now('value'), 4.0)
        self.assertEqual(times.now('value'), 102.0*98.0)
        self.assertEqual(divides.now('value'), 102.0/98.0)



