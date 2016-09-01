
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



