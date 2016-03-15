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
            return True

        def reset(self):
            self.order = None;
            self.price = 0;
            self.qty = 0;

    def setUp(self):
        self.mock = OrderHandlerTest.MockExec()
        self.config = SimConfig()

    def test_limit_order_handler(self):
        handler = LimitOrderHandler(self.mock.execute, self.config)
        self.assertEquals(None, self.mock.order)

        bar1 = Bar(instrument="HSI", open=20, high=21, low=19, close=20.5)
        bar2 = Bar(instrument="HSI", open=16, high=18, low=15, close=17)

        # BUY
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        processed = handler.process_w_price_qty(order, 20, 1000)
        self.assertFalse(processed)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_price_qty(order, 18, 1000)
        self.assertTrue(processed)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(18.5, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()

        # BUY with bar
        processed = handler.process_w_bar(order, bar1)
        self.assertFalse(processed)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_bar(order, bar2)
        self.assertTrue(processed)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(18.5, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()

        # SELL
        order2 = Order(ord_id=1, instrument="HSI", action=OrdAction.SELL, type=OrdType.LIMIT, qty=1000,
                       limit_price=18.5)
        processed = handler.process_w_price_qty(order2, 18, 1000)
        self.assertFalse(processed)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_price_qty(order2, 20, 1000)
        self.assertTrue(processed)
        self.assertEquals(order2, self.mock.order)
        self.assertEquals(18.5, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()

        # SELL with bar
        processed = handler.process_w_bar(order2, bar2)
        self.assertFalse(processed)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_bar(order2, bar1)
        self.assertTrue(processed)
        self.assertEquals(order2, self.mock.order)
        self.assertEquals(18.5, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

    def test_market_order_handler(self):
        handler = MarketOrderHandler(self.mock.execute, self.config)
        self.assertEquals(None, self.mock.order)

        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)

        quote = Quote(instrument="HSI", bid=18, ask=19, bid_size=200, ask_size=500)
        trade = Trade(instrument="HSI", price=20, size=200)

        processed = handler.process_w_price_qty(order, 18, 500)
        self.assertTrue(processed)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(18, self.mock.price)
        self.assertEquals(500, self.mock.qty)

    def test_stop_order_handler(self):
        handler = StopOrderHandler(self.mock.execute, self.config)

        self.assertEquals(None, self.mock.order)

        bar1 = Bar(instrument="HSI", open=20, high=21, low=19, close=20.5)
        bar2 = Bar(instrument="HSI", open=16, high=18, low=15, close=17)

        # BUY
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.STOP, qty=1000, stop_price=18.5)
        processed = handler.process_w_price_qty(order, 18, 1000)
        self.assertFalse(processed)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_price_qty(order, 19, 1000)
        self.assertTrue(processed)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(19, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()

        # BUY with bar
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.STOP, qty=1000, stop_price=18.5)
        processed = handler.process_w_bar(order, bar2)
        self.assertFalse(processed)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_bar(order, bar1)
        self.assertTrue(processed)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(18.5, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()

        # SELL
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.SELL, type=OrdType.STOP, qty=1000, stop_price=18.5)
        processed = handler.process_w_price_qty(order, 19, 1000)
        self.assertFalse(processed)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_price_qty(order, 18, 1000)
        self.assertTrue(processed)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(18, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()

        # SELL with bar
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.SELL, type=OrdType.STOP, qty=1000, stop_price=18.5)
        processed = handler.process_w_bar(order, bar1)
        self.assertFalse(processed)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_bar(order, bar2)
        self.assertTrue(processed)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(18.5, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()

    def test_stop_limit_order_handler(self):
        handler = StopLimitOrderHandler(self.mock.execute, self.config)

        self.assertEquals(None, self.mock.order)

        bar1 = Bar(instrument="HSI", open=20, high=21, low=19, close=20.5)
        bar2 = Bar(instrument="HSI", open=16, high=18, low=15, close=17)

        # BUY
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.STOP_LIMIT, qty=1000, limit_price=18,
                      stop_price=18.5)
        processed = handler.process_w_price_qty(order, 18, 1000)
        self.assertFalse(order.stop_limit_ready)
        self.assertFalse(processed)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_price_qty(order, 19, 1000)
        self.assertTrue(order.stop_limit_ready)
        self.assertFalse(processed)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_price_qty(order, 18, 1000)
        self.assertTrue(order.stop_limit_ready)
        self.assertTrue(processed)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(18, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()

        # BUY with bar
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.STOP_LIMIT, qty=1000, limit_price=18,
                      stop_price=18.5)
        processed = handler.process_w_bar(order, bar2)
        self.assertFalse(processed)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_bar(order, bar1)
        self.assertTrue(order.stop_limit_ready)
        self.assertFalse(processed)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_bar(order, bar2)
        self.assertTrue(order.stop_limit_ready)
        self.assertTrue(processed)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(18, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()
        # SELL
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.SELL, type=OrdType.STOP_LIMIT, qty=1000, limit_price=20,
                      stop_price=18.5)
        processed = handler.process_w_price_qty(order, 19, 1000)
        self.assertFalse(order.stop_limit_ready)
        self.assertFalse(processed)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_price_qty(order, 18, 1000)
        self.assertTrue(order.stop_limit_ready)
        self.assertFalse(processed)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_price_qty(order, 20, 1000)
        self.assertTrue(order.stop_limit_ready)
        self.assertTrue(processed)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(20, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()

        # SELL with bar
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.SELL, type=OrdType.STOP_LIMIT, qty=1000, limit_price=20,
                      stop_price=18.5)
        processed = handler.process_w_bar(order, bar1)
        self.assertFalse(processed)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_bar(order, bar2)
        self.assertTrue(order.stop_limit_ready)
        self.assertFalse(processed)
        self.assertEquals(None, self.mock.order)

        processed = handler.process_w_bar(order, bar1)
        self.assertTrue(order.stop_limit_ready)
        self.assertTrue(processed)
        self.assertEquals(order, self.mock.order)
        self.assertEquals(20, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

    def test_trailing_stop_order_handler(self):
        handler = TrailingStopOrderHandler(self.mock.execute, self.config)

        self.assertEquals(None, self.mock.order)

        bar1 = Bar(instrument="HSI", open=16, high=18, low=15, close=17)
        bar2 = Bar(instrument="HSI", open=17, high=19, low=16, close=18)
        bar3 = Bar(instrument="HSI", open=18, high=20, low=17, close=19)
        bar4 = Bar(instrument="HSI", open=19, high=21, low=18, close=20)
        bar5 = Bar(instrument="HSI", open=20, high=22, low=19, close=21)

        # BUY with bar
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.TRAILING_STOP, qty=1000, stop_price=5)

        self.assertEquals(0, order.trailing_stop_exec_price)

        processed = handler.process_w_bar(order, bar2)
        self.assertEquals(21, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_bar(order, bar3)
        self.assertEquals(21, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_bar(order, bar1)
        self.assertEquals(20, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_bar(order, bar3)
        self.assertEquals(20, order.trailing_stop_exec_price)
        self.assertEquals(order, self.mock.order)
        self.assertTrue(processed)
        self.assertEquals(20, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()


        # BUY
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.TRAILING_STOP, qty=1000, stop_price=5)

        self.assertEquals(0, order.trailing_stop_exec_price)

        processed = handler.process_w_price_qty(order, 16, 1000)
        self.assertEquals(21, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_price_qty(order, 17, 1000)
        self.assertEquals(21, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_price_qty(order, 15, 1000)
        self.assertEquals(20, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_price_qty(order, 19, 1000)
        self.assertEquals(20, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_price_qty(order, 20, 1000)
        self.assertEquals(20, order.trailing_stop_exec_price)
        self.assertEquals(order, self.mock.order)
        self.assertTrue(processed)
        self.assertEquals(20, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()


        # SELL with bar
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.SELL, type=OrdType.TRAILING_STOP, qty=1000, stop_price=5)

        self.assertEquals(0, order.trailing_stop_exec_price)

        processed = handler.process_w_bar(order, bar4)
        self.assertEquals(16, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_bar(order, bar3)
        self.assertEquals(16, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_bar(order, bar5)
        self.assertEquals(17, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_bar(order, bar3)
        self.assertEquals(17, order.trailing_stop_exec_price)
        self.assertEquals(order, self.mock.order)
        self.assertTrue(processed)
        self.assertEquals(17, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()


        # SELL
        order = Order(ord_id=1, instrument="HSI", action=OrdAction.SELL, type=OrdType.TRAILING_STOP, qty=1000, stop_price=5)

        self.assertEquals(0, order.trailing_stop_exec_price)

        processed = handler.process_w_price_qty(order, 21, 1000)
        self.assertEquals(16, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_price_qty(order, 20, 1000)
        self.assertEquals(16, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_price_qty(order, 22, 1000)
        self.assertEquals(17, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_price_qty(order, 18, 1000)
        self.assertEquals(17, order.trailing_stop_exec_price)
        self.assertEquals(None, self.mock.order)
        self.assertFalse(processed)

        processed = handler.process_w_price_qty(order, 17, 1000)
        self.assertEquals(17, order.trailing_stop_exec_price)
        self.assertEquals(order, self.mock.order)
        self.assertTrue(processed)
        self.assertEquals(17, self.mock.price)
        self.assertEquals(1000, self.mock.qty)

        self.mock.reset()