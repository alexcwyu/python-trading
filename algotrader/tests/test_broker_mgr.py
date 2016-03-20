from unittest import TestCase

from algotrader.provider.broker.simulator import Simulator
from algotrader.provider import BrokerManager


class BrokerManagerTest(TestCase):
    def test_reg(self):
        bm = BrokerManager()
        self.assertIsNone(bm.get_broker("Simulator"))

        bm.reg_broker(Simulator())
        self.assertIsNotNone(bm.get_broker("Simulator"))
