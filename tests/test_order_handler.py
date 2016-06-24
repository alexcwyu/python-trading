from unittest import TestCase

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.event.order import Order, OrdAction, OrdType
from algotrader.provider.broker.sim.order_handler import LimitOrderHandler, MarketOrderHandler, StopLimitOrderHandler, \
    StopOrderHandler, TrailingStopOrderHandler
from algotrader.provider.broker.sim.sim_config import SimConfig


class OrderHandlerTest(TestCase):
    def setUp(self):
        self.config = SimConfig(bar_vol_ratio=1)

    def test_limit_order_handler(self):
        handler = LimitOrderHandler(self.config)

        bar1 = Bar(inst_id=1, open=20, high=21, low=19, close=20.5, vol=1000)
        bar2 = Bar(inst_id=1, open=16, high=18, low=15, close=17, vol=1000)

        # BUY
        order = Order(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        fill_info = handler.process_w_price_qty(order, 20, 1000)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 18, 1000)
        self.assertEquals(18.5, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # BUY with bar
        fill_info = handler.process(order, bar1)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar2)
        self.assertEquals(18.5, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL
        order2 = Order(ord_id=1, inst_id=1, action=OrdAction.SELL, type=OrdType.LIMIT, qty=1000,
                       limit_price=18.5)
        fill_info = handler.process_w_price_qty(order2, 18, 1000)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order2, 20, 1000)
        self.assertEquals(18.5, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL with bar
        fill_info = handler.process(order2, bar2)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order2, bar1)
        self.assertEquals(18.5, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

    def test_market_order_handler(self):
        handler = MarketOrderHandler(self.config)

        order = Order(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)

        quote = Quote(inst_id=1, bid=18, ask=19, bid_size=200, ask_size=500)
        trade = Trade(inst_id=1, price=20, size=200)

        fill_info = handler.process_w_price_qty(order, 18, 500)
        self.assertEquals(18, fill_info.fill_price)
        self.assertEquals(500, fill_info.fill_qty)

    def test_stop_order_handler(self):
        handler = StopOrderHandler(self.config)

        bar1 = Bar(inst_id=1, open=20, high=21, low=19, close=20.5, vol=1000)
        bar2 = Bar(inst_id=1, open=16, high=18, low=15, close=17, vol=1000)

        # BUY
        order = Order(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.STOP, qty=1000, stop_price=18.5)
        fill_info = handler.process_w_price_qty(order, 18, 1000)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 19, 1000)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(19, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # BUY with bar
        order = Order(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.STOP, qty=1000, stop_price=18.5)
        fill_info = handler.process(order, bar2)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar1)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(18.5, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL
        order = Order(ord_id=1, inst_id=1, action=OrdAction.SELL, type=OrdType.STOP, qty=1000, stop_price=18.5)
        fill_info = handler.process_w_price_qty(order, 19, 1000)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 18, 1000)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(18, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL with bar
        order = Order(ord_id=1, inst_id=1, action=OrdAction.SELL, type=OrdType.STOP, qty=1000, stop_price=18.5)
        fill_info = handler.process(order, bar1)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar2)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(18.5, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

    def test_stop_limit_order_handler(self):
        handler = StopLimitOrderHandler(self.config)

        bar1 = Bar(inst_id=1, open=20, high=21, low=19, close=20.5, vol=1000)
        bar2 = Bar(inst_id=1, open=16, high=18, low=15, close=17, vol=1000)

        # BUY
        order = Order(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.STOP_LIMIT, qty=1000,
                      limit_price=18,
                      stop_price=18.5)
        fill_info = handler.process_w_price_qty(order, 18, 1000)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 19, 1000)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 18, 1000)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(18, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # BUY with bar
        order = Order(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.STOP_LIMIT, qty=1000,
                      limit_price=18,
                      stop_price=18.5)
        fill_info = handler.process(order, bar2)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar1)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar2)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(18, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL
        order = Order(ord_id=1, inst_id=1, action=OrdAction.SELL, type=OrdType.STOP_LIMIT, qty=1000,
                      limit_price=20,
                      stop_price=18.5)
        fill_info = handler.process_w_price_qty(order, 19, 1000)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 18, 1000)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 20, 1000)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(20, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL with bar
        order = Order(ord_id=1, inst_id=1, action=OrdAction.SELL, type=OrdType.STOP_LIMIT, qty=1000,
                      limit_price=20,
                      stop_price=18.5)
        fill_info = handler.process(order, bar1)
        self.assertFalse(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar2)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar1)
        self.assertTrue(order.stop_limit_ready)
        self.assertEquals(20, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

    def test_trailing_stop_order_handler(self):
        handler = TrailingStopOrderHandler(self.config)

        bar1 = Bar(inst_id=1, open=16, high=18, low=15, close=17, vol=1000)
        bar2 = Bar(inst_id=1, open=17, high=19, low=16, close=18, vol=1000)
        bar3 = Bar(inst_id=1, open=18, high=20, low=17, close=19, vol=1000)
        bar4 = Bar(inst_id=1, open=19, high=21, low=18, close=20, vol=1000)
        bar5 = Bar(inst_id=1, open=20, high=22, low=19, close=21, vol=1000)

        # BUY with bar
        order = Order(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.TRAILING_STOP, qty=1000,
                      stop_price=5)

        self.assertEquals(0, order.trailing_stop_exec_price)

        fill_info = handler.process(order, bar2)
        self.assertEquals(21, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar3)
        self.assertEquals(21, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar1)
        self.assertEquals(20, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar3)
        self.assertEquals(20, order.trailing_stop_exec_price)
        self.assertEquals(20, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # BUY
        order = Order(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.TRAILING_STOP, qty=1000,
                      stop_price=5)

        self.assertEquals(0, order.trailing_stop_exec_price)

        fill_info = handler.process_w_price_qty(order, 16, 1000)
        self.assertEquals(21, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 17, 1000)
        self.assertEquals(21, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 15, 1000)
        self.assertEquals(20, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 19, 1000)
        self.assertEquals(20, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 20, 1000)
        self.assertEquals(20, order.trailing_stop_exec_price)
        self.assertEquals(20, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL with bar
        order = Order(ord_id=1, inst_id=1, action=OrdAction.SELL, type=OrdType.TRAILING_STOP, qty=1000,
                      stop_price=5)

        self.assertEquals(0, order.trailing_stop_exec_price)

        fill_info = handler.process(order, bar4)
        self.assertEquals(16, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar3)
        self.assertEquals(16, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar5)
        self.assertEquals(17, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order, bar3)
        self.assertEquals(17, order.trailing_stop_exec_price)
        self.assertEquals(17, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL
        order = Order(ord_id=1, inst_id=1, action=OrdAction.SELL, type=OrdType.TRAILING_STOP, qty=1000,
                      stop_price=5)

        self.assertEquals(0, order.trailing_stop_exec_price)

        fill_info = handler.process_w_price_qty(order, 21, 1000)
        self.assertEquals(16, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 20, 1000)
        self.assertEquals(16, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 22, 1000)
        self.assertEquals(17, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 18, 1000)
        self.assertEquals(17, order.trailing_stop_exec_price)
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order, 17, 1000)
        self.assertEquals(17, order.trailing_stop_exec_price)
        self.assertEquals(17, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)
