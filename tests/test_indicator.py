from unittest import TestCase

from algotrader.utils.data_series_utils import DataSeriesUtils
from algotrader.config.app import ApplicationConfig
from algotrader.trading.context import ApplicationContext


class IndicatorTest(TestCase):
    def setUp(self):
        self.app_config = ApplicationConfig(None, None, None, None, None, None, None)
        self.app_context = ApplicationContext(app_config=self.app_config)
        self.utils = DataSeriesUtils(self.app_context)


    def test_reuse(self):
        close = self.app_context.inst_data_mgr.get_series("bar")
        close.start(self.app_context)

        sma1 = self.utils.get_or_create_indicator("SMA", 'bar', 'close', 3)
        sma1.start(self.app_context)

        sma2 = self.utils.get_or_create_indicator("SMA", 'bar', 'close', 3)
        sma2.start(self.app_context)

        sma3 = self.utils.get_or_create_indicator("SMA", 'bar', 'close', 10)
        sma3.start(self.app_context)

        self.assertEquals(sma1, sma2)
        self.assertNotEquals(sma2, sma3)
        self.assertNotEquals(sma1, sma3)

        sma4 = self.utils.get_or_create_indicator("SMA", "SMA('bar',close,3)", 10)
        sma4.start(self.app_context)

        self.assertEquals(sma4.input, sma2)

    def test_parse(self):
        bar = self.utils.parse("bar")
        bar.start(self.app_context)

        sma1 = self.utils.parse("SMA('bar',close,3)")
        sma1.start(self.app_context)

        sma2 = self.utils.parse("SMA(SMA('bar',close,3),value,10)")
        sma2.start(self.app_context)

        rsi = self.utils.parse("RSI(SMA(SMA('bar',close,3),value,10),value,14, 9)")
        rsi.start(self.app_context)

        self.assertEquals(sma1.input, bar)
        self.assertEquals(3, sma1.length)

        self.assertEquals(sma2.input, sma1)
        self.assertEquals(10, sma2.length)

        self.assertEquals(rsi.input, sma2)
        self.assertEquals(14, rsi.length)

    def test_fail_parse(self):
        with self.assertRaises(AssertionError):
            self.utils.parse("SMA('Bar.Close',3")

        with self.assertRaises(AssertionError):
            self.utils.parse("RSI(SMA(SMA('Bar.Close',3,10),14)")
