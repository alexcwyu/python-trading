from datetime import datetime
from unittest import TestCase

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.technical.ma import *
import numpy as np


class MovingAverageTest(TestCase):
    def test_name(self):
        close = TimeSeries("close")
        sma = SMA(close, 3)
        self.assertEquals("SMA(close,3)", sma.id)

    def test_empty_at_initialize(self):
        close = TimeSeries("close")
        sma = SMA(close, 3)
        self.assertEquals(0, len(sma.get_data()))

    def test_nan_before_size(self):
        close = TimeSeries("close")
        sma = SMA(close, 3)
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)
        t3 = t2 + datetime.timedelta(0, 3)

        close.add(t1, 2)
        self.assertEquals((t1, np.nan), sma.get_data())

        close.add(t2, 2.4)
        self.assertEquals((t2, np.nan), sma.get_data())

        close.add(t3, 2.8)
        t, v = sma.get_data()
        self.assertEquals(t2, t)
        self.assertNotEquals(np.nan, v)

    def test_moving_average_calculation(self):
        close = TimeSeries("close")
        sma = SMA(close, 3)

        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)
        t3 = t2 + datetime.timedelta(0, 3)
        t4 = t3 + datetime.timedelta(0, 3)
        t5 = t4 + datetime.timedelta(0, 3)

        close.add(t1, 2)
        self.assertEquals((t1, np.nan), sma.current_value())
        close.add(t2, 2.4)
        self.assertEquals((t2, np.nan), sma.current_value())
        close.add(t3, 2.8)
        self.assertEquals((t3, 2.4), sma.current_value())
        close.add(t4, 3.2)
        self.assertEquals((t4, 2.8), sma.current_value())
        close.add(t5, 3.6)
        self.assertEquals((t5, 3.2), sma.current_value())

        self.assertEquals((t1, np.nan), sma.get_value_by_idx(0))
        self.assertEquals((t2, np.nan), sma.get_value_by_idx(1))
        self.assertEquals((t3, 2.4), sma.get_value_by_idx(2))
        self.assertEquals((t4, 2.8), sma.get_value_by_idx(3))
        self.assertEquals((t5, 3.2), sma.get_value_by_idx(4))

        self.assertEquals((t1, np.nan), sma.get_value_by_time(t1))
        self.assertEquals((t2, np.nan), sma.get_value_by_time(t2))
        self.assertEquals((t3, 2.4), sma.get_value_by_time(t3))
        self.assertEquals((t4, 2.8), sma.get_value_by_time(t4))
        self.assertEquals((t5, 3.2), sma.get_value_by_time(t5))
