
import math

import talib
from datetime import datetime
from unittest import TestCase
import numpy as np
import datetime
from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
from algotrader.technical.pipeline.rank import Rank
from algotrader.technical.pipeline.cross_sessional_apply import Average
from algotrader.technical.pipeline.cross_sessional_apply import Sum as GSSum
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


    # def test_nan_before_size(self):
    def test_with_multiple_bar(self):
        inst_data_mgr.clear()
        bar0 = inst_data_mgr.get_series("bar0")
        bar1 = inst_data_mgr.get_series("bar1")
        bar2 = inst_data_mgr.get_series("bar2")
        bar3 = inst_data_mgr.get_series("bar3")

        rank = Rank([bar0, bar1, bar2, bar3], input_key='close')
        avg = Average([bar0, bar1, bar2, bar3], input_key='close')
        gssum = GSSum([bar0, bar1, bar2, bar3], input_key='close')

        t1 = datetime.datetime.now()
        bar0.add({"timestamp": t1, "close": 80.0, "open": 0})
        bar1.add({"timestamp": t1, "close": 95.0, "open": 0})
        bar2.add({"timestamp": t1, "close": 102.0, "open": 0})
        bar3.add({"timestamp": t1, "close": 105.0, "open": 0})

        # self.assertEquals([{"timestamp": t1,
        #                     "name": "'Rank('bar0','bar1','bar2','bar3',close)'",
        #                     "value": np.arange(4)/3.0}],
        #                   rank.get_data())

        rank_target = np.arange(4)/3.0
        rank_target = rank_target.reshape((1,4))
        avg_target = np.array([[95.5]])
        sum_target = np.array([[382.0]])

        try:
            np.testing.assert_almost_equal(rank_target, rank.get_data()[0]["value"], 5)
            np.testing.assert_almost_equal(avg_target, avg.get_data()[0]["value"], 5)
            np.testing.assert_almost_equal(sum_target, gssum.get_data()[0]["value"], 5)
        except AssertionError as e:
            self.fail(e.message)

    def test_with_multi_bar_multi_indicator(self):
        inst_data_mgr.clear()
        bar0 = inst_data_mgr.get_series("bar0")
        bar1 = inst_data_mgr.get_series("bar1")

        sma_2_bar0 = SMA(bar0, "close", 2)
        sma_4_bar0 = SMA(bar0, "close", 4)
        sma_3_bar1 = SMA(bar1, "close", 3)

        rank = Rank([sma_2_bar0, sma_3_bar1, sma_4_bar0], input_key=Indicator.VALUE)

        t = datetime.datetime.now()
        bar0.add({"timestamp": t, "close": 80.0, "open": 0})
        bar1.add({"timestamp": t, "close": 95.0, "open": 0})
        print rank.now(keys=PipeLine.VALUE)

        t = t + datetime.timedelta(0, 3)
        bar0.add({"timestamp": t, "close": 85.0, "open": 0})
        bar1.add({"timestamp": t, "close": 93.0, "open": 0})
        print rank.now(keys=PipeLine.VALUE)

        t = t + datetime.timedelta(0, 3)
        bar0.add({"timestamp": t, "close": 86.0, "open": 0})
        bar1.add({"timestamp": t, "close": 91.0, "open": 0})
        print rank.now(keys=PipeLine.VALUE)

        t = t + datetime.timedelta(0, 3)
        bar0.add({"timestamp": t, "close": 90.0, "open": 0})
        bar1.add({"timestamp": t, "close": 95.0, "open": 0})
        print rank.now(keys=PipeLine.VALUE)
