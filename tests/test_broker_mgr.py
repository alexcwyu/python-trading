from unittest import TestCase

from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.provider import BrokerManager


class BrokerManagerTest(TestCase):
    def test_reg(self):
        bm = BrokerManager()
        self.assertIsNone(bm.get("Simulator"))

        bm.register(Simulator())
        self.assertIsNotNone(bm.get("Simulator"))
