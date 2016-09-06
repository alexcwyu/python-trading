
import math
import talib
from datetime import datetime
from unittest import TestCase
import numpy as np
import datetime
from algotrader.technical.pipeline.rank import Rank
from algotrader.technical.talib_wrapper import SMA
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.utils.time_series import DataSeries


class PipelineTest(TestCase):
    def test_name(self):
        inst_data_mgr.clear()
        bar = inst_data_mgr.get_series("bar")
        sma3 = SMA(bar, input_key='close', length=3)
        sma20 = SMA(bar, input_key='close', length=20)
        sma50 = SMA(bar, input_key='close', length=50)

        rank = Rank([sma3, sma20, sma50], input_key='close')
        self.assertEquals("Rank(SMA('bar',close,3),SMA('bar',close,20),SMA('bar',close,50),close)",
            rank.name)

    def test_empty_at_initialize(self):
        inst_data_mgr.clear()
        close = inst_data_mgr.get_series("bar")
        sma3 = SMA(close, input_key='close', length=3)
        sma20 = SMA(close, input_key='close', length=20)
        sma50 = SMA(close, input_key='close', length=50)

        rank = Rank([sma3, sma20, sma50], input_key='close')
        self.assertEquals(0, len(rank.get_data()))

    def test_shape(self):
        inst_data_mgr.clear()
        close = inst_data_mgr.get_series("bar")
        sma3 = SMA(close, input_key='close', length=3)
        sma20 = SMA(close, input_key='close', length=20)
        sma50 = SMA(close, input_key='close', length=50)

        rank = Rank([sma3, sma20, sma50], input_key='close')
        try:
            np.testing.assert_almost_equal(np.array([1, 3]), rank.shape(), 5)
        except AssertionError as e:
            self.fail(e.message)


    def test_nan_before_size(self):
        inst_data_mgr.clear()
        bar0 = inst_data_mgr.get_series("bar0")
        bar1 = inst_data_mgr.get_series("bar1")
        bar2 = inst_data_mgr.get_series("bar2")
        bar3 = inst_data_mgr.get_series("bar3")

        rank = Rank([bar0, bar1, bar2, bar3], input_key='close')

        t1 = datetime.datetime.now()
        bar0.add({"timestamp": t1, "close": 80.0, "open": 0})
        bar1.add({"timestamp": t1, "close": 95.0, "open": 0})
        bar2.add({"timestamp": t1, "close": 102.0, "open": 0})
        bar3.add({"timestamp": t1, "close": 105.0, "open": 0})

        self.assertEquals([{"timestamp": t1, 'value': np.arange(4)/3.0}],
                          rank.get_data())



