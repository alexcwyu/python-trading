from unittest import TestCase

from algotrader.provider import BrokerManager
from algotrader.provider.broker.sim.simulator import Simulator


class BrokerManagerTest(TestCase):
    def test_reg(self):
        bm = BrokerManager()
        self.assertIsNone(bm.get("Simulator"))

        bm.register(Simulator())
        self.assertIsNotNone(bm.get("Simulator"))
