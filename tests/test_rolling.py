import numpy as np
from unittest import TestCase

from algotrader.technical.rolling_apply import StdDev
from algotrader.trading.context import ApplicationContext


# from algotrader.trading.instrument_data import inst_data_mgr


class RollingApplyTest(TestCase):
    def setUp(self):
        self.app_context = ApplicationContext()

    def test_name(self):
        bar = self.app_context.inst_data_mgr.get_series("bar")
        stddev = StdDev(inputs=bar, input_keys='close', length=3)
        self.assertEquals("StdDev(bar[close],length=3)", stddev.name)

    def test_empty_at_initialize(self):
        close = self.app_context.inst_data_mgr.get_series("bar")
        stddev = StdDev(inputs=close, input_keys='close', length=3)
        self.assertEquals(0, len(stddev.get_data()))

    def test_nan_before_size(self):
        bar = self.app_context.inst_data_mgr.get_series("bar")
        bar.start(self.app_context)

        stddev = StdDev(inputs=bar, input_keys='close', length=3)
        stddev.start(self.app_context)

        t1 = 1

        nextTime = lambda t: t + 3

        x = np.random.normal(0, 2.0, 3)
        ts = np.cumsum(x) + 100

        i = 0

        bar.add(timestamp=t1, data={"close": ts[i], "open": 0})
        self.assertEquals([{'value': np.nan}],
                          stddev.get_data())

        t2 = nextTime(t1)
        i = i + 1
        bar.add(timestamp=t2, data={"close": ts[i], "open": 1.4})
        self.assertEquals([{'value': np.nan},
                           {'value': np.nan}],
                          stddev.get_data())

        t3 = nextTime(t2)
        i = i + 1
        bar.add(timestamp=t3, data={"close": ts[i], "open": 1.8})
        self.assertEquals([{'value': np.nan},
                           {'value': np.nan},
                           {'value': np.std(ts)}],
                          stddev.get_data())

        # def test_moving_average_calculation(self):
        #     inst_data_mgr.clear()
        #     bar = inst_data_mgr.get_series("bar")
        #     sma = SMA(bar, input_key='close', length=3)
        #
        #     t1 = datetime.datetime.now()
        #     t2 = t1 + datetime.timedelta(0, 3)
        #     t3 = t2 + datetime.timedelta(0, 3)
        #     t4 = t3 + datetime.timedelta(0, 3)
        #     t5 = t4 + datetime.timedelta(0, 3)
        #
        #     bar.add({"timestamp": t1, "close": 2.0, "open": 0})
        #     self.assertTrue(math.isnan(sma.now('value')))
        #
        #     bar.add({"timestamp": t2, "close": 2.4, "open": 1.4})
        #     self.assertTrue(math.isnan(sma.now('value')))
        #
        #     bar.add({"timestamp": t3, "close": 2.8, "open": 1.8})
        #     self.assertEquals(2.4, sma.now('value'))
        #
        #     bar.add({"timestamp": t4, "close": 3.2, "open": 2.2})
        #     self.assertEquals(2.8, sma.now('value'))
        #
        #     bar.add({"timestamp": t5, "close": 3.6, "open": 2.6})
        #     self.assertEquals(3.2, sma.now('value'))
        #
        #     self.assertTrue(math.isnan(sma.get_by_idx(0, 'value')))
        #     self.assertTrue(math.isnan(sma.get_by_idx(1, 'value')))
        #     self.assertEquals(2.4, sma.get_by_idx(2, 'value'))
        #     self.assertEquals(2.8, sma.get_by_idx(3, 'value'))
        #     self.assertEquals(3.2, sma.get_by_idx(4, 'value'))
        #
        #     self.assertTrue(math.isnan(sma.get_by_time(t1, 'value')))
        #     self.assertTrue(math.isnan(sma.get_by_time(t2, 'value')))
        #     self.assertEquals(2.4, sma.get_by_time(t3, 'value'))
        #     self.assertEquals(2.8, sma.get_by_time(t4, 'value'))
        #     self.assertEquals(3.2, sma.get_by_time(t5, 'value'))
