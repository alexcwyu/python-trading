from datetime import datetime
from unittest import TestCase

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.provider.broker import SimConfig, Simulator, LimitOrderHandler, MarketOrderHandler, StopLimitOrderHandler, StopOrderHandler, TrailingStopOrderHandler


class OrderHandlerTest(TestCase):
    def test_limit_order_handler(self):

        config = SimConfig()
        simulator = Simulator()
        handler = LimitOrderHandler()

    def test_market_order_handler(self):
        pass

    def test_stop_order_handler(self):
        pass

    def test_stop_limit_order_handler(self):
        pass

    def test_trailing_stop_order_handler(self):
        pass