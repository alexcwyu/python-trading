from unittest import TestCase

from algotrader.provider.broker import Broker
from algotrader.provider import ProviderManager


class BrokerManagerTest(TestCase):
    def test_reg(self):
        bm = ProviderManager()
        self.assertIsNotNone(bm.get(Broker.Simulator))
