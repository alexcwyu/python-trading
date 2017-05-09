from unittest import TestCase

from algotrader.utils.data_series import *


class DataSeriesUtilsTest(TestCase):
    def test_build_series_name(self):
        name = build_series_id("SMA")
        self.assertEqual("SMA()", name)

        name = build_series_id("SMA", inputs='Bar.HSI')
        self.assertEqual("SMA(Bar.HSI)", name)

        name = build_series_id("SMA", input_keys='Close')
        self.assertEqual("SMA()", name)

        name = build_series_id("SMA", length=10, vol=2)
        self.assertTrue(name in set(["SMA(length=10,vol=2)", "SMA(vol=2,length=10)"]))

        name = build_series_id("SMA", inputs='Bar.HSI', input_keys='Close', length=10)
        self.assertEqual("SMA(Bar.HSI[Close],length=10)", name)

        name = build_series_id("SMA", inputs='Bar.HSI', input_keys=['Close', 'Open'], length=10)
        self.assertEqual("SMA(Bar.HSI[Close,Open],length=10)", name)

        name = build_series_id("SMA", inputs=['Bar.HSI', 'Quote.SPX'], input_keys=['Close', 'Open'], length=1)

        self.assertEqual("SMA(Bar.HSI[Close,Open],Quote.SPX[Close,Open],length=1)", name)

        name = build_series_id("SMA", inputs='SMA(Bar.HSI[Close],length=10)', length=5)
        self.assertEqual("SMA(SMA(Bar.HSI[Close],length=10),length=5)", name)
