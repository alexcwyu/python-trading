import datetime
import numpy as np
from datetime import datetime
from unittest import TestCase

from algotrader.technical.pipeline.pairwise import Plus, Minus, Times, Divides, PairCorrelation
from algotrader.trading.context import ApplicationContext


class PairwiseTest(TestCase):
    def setUp(self):
        self.app_context = ApplicationContext()

    def test_name(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")

        bar0.start(self.app_context)
        bar1.start(self.app_context)

        bar0_plus_bar1 = Plus(inputs=[bar0, bar1], input_keys='close')
        bar0_plus_bar1.start(self.app_context)

        self.assertEquals("Plus(bar0[close],bar1[close],length=1)",
                          bar0_plus_bar1.name)

        spread = Minus(inputs=[bar0, bar1], input_keys='close')
        spread.start(self.app_context)

        self.assertEquals("Minus(bar0[close],bar1[close],length=1)",
                          spread.name)

    def test_empty_at_initialize(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")

        bar0.start(self.app_context)
        bar1.start(self.app_context)

        bar0_plus_bar1 = Plus(inputs=[bar0, bar1], input_keys='close')
        bar0_plus_bar1.start(self.app_context)

        self.assertEquals(0, len(bar0_plus_bar1.get_data()))

    def test_shape(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")

        bar0.start(self.app_context)
        bar1.start(self.app_context)

        bar0_plus_bar1 = Plus(inputs=[bar0, bar1], input_keys='close')
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

        plus = Plus(inputs=[bar0, bar1], input_keys='close')
        minus = Minus(inputs=[bar0, bar1], input_keys='close')
        times = Times(inputs=[bar0, bar1], input_keys='close')
        divides = Divides(inputs=[bar0, bar1], input_keys='close')
        pcorr = PairCorrelation(inputs=[bar0, bar1], input_keys='close', length=4)

        plus.start(self.app_context)
        minus.start(self.app_context)
        times.start(self.app_context)
        divides.start(self.app_context)
        pcorr.start(self.app_context)

        now = 1
        x = np.array([80.0, 102.0, 101.0, 99.0])
        y = np.array([95.0, 98.0, 105.2, 103.3])
        ts = [now + 3 for i in range(4)]
        x_p_y = x + y
        x_m_y = x - y
        x_t_y = x * y
        x_d_y = x / y

        bar0.add(data={"timestamp": ts[0], "close": x[0], "open": 0})
        bar1.add(data={"timestamp": ts[0], "close": y[0], "open": 0})

        self.assertEqual(plus.now('value'), 175.0)
        self.assertEqual(minus.now('value'), -15.0)
        self.assertEqual(times.now('value'), 7600.0)
        self.assertEqual(divides.now('value'), 80.0 / 95.0)

        bar0.add(data={"timestamp": ts[1], "close": x[1], "open": 0})
        bar1.add(data={"timestamp": ts[1], "close": y[1], "open": 0})

        self.assertEqual(plus.now('value'), 200.0)
        self.assertEqual(minus.now('value'), 4.0)
        self.assertEqual(times.now('value'), 102.0 * 98.0)
        self.assertEqual(divides.now('value'), 102.0 / 98.0)

        bar0.add(data={"timestamp": ts[2], "close": x[2], "open": 0})
        bar1.add(data={"timestamp": ts[2], "close": y[2], "open": 0})

        bar0.add(data={"timestamp": ts[3], "close": x[3], "open": 0})
        bar1.add(data={"timestamp": ts[3], "close": y[3], "open": 0})

        self.assertEqual(pcorr.now('value'), np.corrcoef(x, y)[0, 1])
