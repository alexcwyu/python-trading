from unittest import TestCase

from algotrader.technical import get_or_create_indicator, parse
from algotrader.trading.instrument_data import inst_data_mgr


class IndicatorTest(TestCase):
    def test_reuse(self):
        close = inst_data_mgr.get_series("bar")
        sma1 = get_or_create_indicator("SMA", 'bar', 'close', 3)
        sma2 = get_or_create_indicator("SMA", 'bar', 'close', 3)
        sma3 = get_or_create_indicator("SMA", 'bar', 'close', 10)

        self.assertEquals(sma1, sma2)
        self.assertNotEquals(sma2, sma3)
        self.assertNotEquals(sma1, sma3)

        sma4 = get_or_create_indicator("SMA", "SMA('bar',close,3)", 10)
        self.assertEquals(sma4.input, sma2)

    def test_parse(self):
        bar = parse("bar")
        sma1 = parse("SMA('bar',close,3)")
        sma2 = parse("SMA(SMA('bar',close,3),value,10)")
        rsi = parse("RSI(SMA(SMA('bar',close,3),value,10),value,14, 9)")

        self.assertEquals(sma1.input, bar)
        self.assertEquals(3, sma1.length)

        self.assertEquals(sma2.input, sma1)
        self.assertEquals(10, sma2.length)

        self.assertEquals(rsi.input, sma2)
        self.assertEquals(14, rsi.length)

    def test_fail_parse(self):
        with self.assertRaises(AssertionError):
            parse("SMA('Bar.Close',3")

        with self.assertRaises(AssertionError):
            parse("RSI(SMA(SMA('Bar.Close',3,10),14)")
