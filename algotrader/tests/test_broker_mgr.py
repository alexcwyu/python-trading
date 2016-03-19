from unittest import TestCase

from algotrader.provider.broker import Simulator
from algotrader.provider.broker_mgr import BrokerManager


class BrokerManagerTest(TestCase):
    def test_reg(self):
        bm = BrokerManager()
        self.assertIsNone(bm.get_broker("Simulator"))

        bm.reg_broker(Simulator())
        self.assertIsNotNone(bm.get_broker("Simulator"))
