from unittest import TestCase

from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.provider_mgr import ProviderManager
from algotrader.provider.broker import Broker

class BrokerManagerTest(TestCase):
    def test_reg(self):
        bm = ProviderManager()
        self.assertIsNotNone(bm.get(Broker.Simulator))
