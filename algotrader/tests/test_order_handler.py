from unittest import TestCase

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.event.order import Order, OrdAction, OrdType
from algotrader.provider.broker import SimConfig, LimitOrderHandler, MarketOrderHandler, StopLimitOrderHandler, StopOrderHandler, TrailingStopOrderHandler


class OrderHandlerTest(TestCase):
    class MockExec():
        def __init__(self):
            self.order = None;
            self.price = 0;
            self.qty = 0;

        def execute(self, order, price, qty):
            self.order = order
            self.price = price
            self.qty = qty

    def setUp(self):
        self.mock = OrderHandlerTest.MockExec()
        self.config = SimConfig()

    def test_limit_order_handler(self):
        handler = LimitOrderHandler(self.mock.execute, self.config)

    def test_market_order_handler(self):
        handler = MarketOrderHandler(self.mock.execute, self.config)

        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)

        bar = Bar(instrument="HSI", open=18, high=19, low=17, close=17.5)
        quote = Quote(instrument="HSI", bid=18, ask=19, bid_size=200, ask_size=500)
        trade = Trade(instrument="HSI", price=20, size=200)

        handler.process_w_price_qty(order, 18, 500)

        self.assertEquals(order, self.mock.order)
        self.assertEquals(18, self.mock.price)
        self.assertEquals(500, self.mock.qty)


    def test_stop_order_handler(self):
        handler = StopOrderHandler(self.mock.execute, self.config)

    def test_stop_limit_order_handler(self):
        handler = StopLimitOrderHandler(self.mock.execute, self.config)

    def test_trailing_stop_order_handler(self):
        handler = TrailingStopOrderHandler(self.mock.execute, self.config)
