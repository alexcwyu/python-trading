from unittest import TestCase

from algotrader.utils.model import *


class ModelUtilsTest(TestCase):

    def test_get_full_cls_name(self):
        from algotrader.technical.ma import SMA
        ma = SMA(inputs="null")
        self.assertEqual("algotrader.technical.ma.SMA", get_full_cls_name(ma))

        self.assertEqual("algotrader.technical.ma.SMA", get_full_cls_name(SMA))


    def test_dynamic_import(self):
        bb = get_cls("algotrader.technical.ma.SMA")(inputs="null")

        self.assertEqual("algotrader.technical.ma.SMA", get_full_cls_name(bb))
