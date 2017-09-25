from unittest import TestCase

from algotrader.model.model_factory import ModelFactory
from algotrader.model.trade_data_pb2 import *
from algotrader.provider.broker.sim.order_handler import LimitOrderHandler, MarketOrderHandler, StopLimitOrderHandler, \
    StopOrderHandler, TrailingStopOrderHandler
from algotrader.provider.broker.sim.sim_config import SimConfig


class OrderHandlerTest(TestCase):
    def setUp(self):
        self.config = SimConfig(bar_vol_ratio=1)

    def test_limit_order_handler(self):
        handler = LimitOrderHandler(self.config)

        bar1 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=20, high=21, low=19, close=20.5, volume=1000)
        bar2 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=16, high=18, low=15, close=17, volume=1000)

        # BUY
        order = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="1", inst_id="1", action=Buy,
                                                     type=Limit,
                                                     qty=1000, limit_price=18.5)
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
        order2 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="2", inst_id="1",
                                                      action=Sell, type=Limit,
                                                      qty=1000,
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

        order = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="1", inst_id="1", action=Buy,
                                                     type=Limit,
                                                     qty=1000, limit_price=18.5)

        quote = ModelFactory.build_quote(timestamp=0, inst_id="1", bid=18, ask=19, bid_size=200, ask_size=500)
        trade = ModelFactory.build_trade(timestamp=0, inst_id="1", price=20, size=200)

        fill_info = handler.process_w_price_qty(order, 18, 500)
        self.assertEquals(18, fill_info.fill_price)
        self.assertEquals(500, fill_info.fill_qty)

    def test_stop_order_handler(self):
        handler = StopOrderHandler(self.config)

        bar1 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=20, high=21, low=19, close=20.5, volume=1000)
        bar2 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=16, high=18, low=15, close=17, volume=1000)

        # BUY
        order1 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="1", inst_id="1", action=Buy,
                                                      type=Stop,
                                                      qty=1000, stop_price=18.5)
        fill_info = handler.process_w_price_qty(order1, 18, 1000)
        self.assertFalse(handler.stop_limit_ready(order1.cl_id, order1.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order1, 19, 1000)
        self.assertTrue(handler.stop_limit_ready(order1.cl_id, order1.cl_ord_id))
        self.assertEquals(19, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # BUY with bar
        order2 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="2", inst_id="1", action=Buy,
                                                      type=Stop,
                                                      qty=1000, stop_price=18.5)
        fill_info = handler.process(order2, bar2)
        self.assertFalse(handler.stop_limit_ready(order2.cl_id, order2.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order2, bar1)
        self.assertTrue(handler.stop_limit_ready(order2.cl_id, order2.cl_ord_id))
        self.assertEquals(18.5, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL
        order3 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="3", inst_id="1",
                                                      action=Sell, type=Stop,
                                                      qty=1000, stop_price=18.5)
        fill_info = handler.process_w_price_qty(order3, 19, 1000)
        self.assertFalse(handler.stop_limit_ready(order3.cl_id, order3.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order3, 18, 1000)
        self.assertTrue(handler.stop_limit_ready(order3.cl_id, order3.cl_ord_id))
        self.assertEquals(18, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL with bar
        order4 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="4", inst_id="1",
                                                      action=Sell, type=Stop,
                                                      qty=1000, stop_price=18.5)
        fill_info = handler.process(order4, bar1)
        self.assertFalse(handler.stop_limit_ready(order4.cl_id, order4.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order4, bar2)
        self.assertTrue(handler.stop_limit_ready(order4.cl_id, order4.cl_ord_id))
        self.assertEquals(18.5, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

    def test_StopLimit_order_handler(self):
        handler = StopLimitOrderHandler(self.config)

        bar1 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=20, high=21, low=19, close=20.5, volume=1000)
        bar2 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=16, high=18, low=15, close=17, volume=1000)

        # BUY
        order1 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="1", inst_id="1", action=Buy,
                                                      type=StopLimit,
                                                      qty=1000,
                                                      limit_price=18,
                                                      stop_price=18.5)
        fill_info = handler.process_w_price_qty(order1, 18, 1000)
        self.assertFalse(handler.stop_limit_ready(order1.cl_id, order1.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order1, 19, 1000)
        self.assertTrue(handler.stop_limit_ready(order1.cl_id, order1.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order1, 18, 1000)
        self.assertTrue(handler.stop_limit_ready(order1.cl_id, order1.cl_ord_id))
        self.assertEquals(18, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # BUY with bar
        order2 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="2", inst_id="1", action=Buy,
                                                      type=StopLimit,
                                                      qty=1000,
                                                      limit_price=18,
                                                      stop_price=18.5)
        fill_info = handler.process(order2, bar2)
        self.assertFalse(handler.stop_limit_ready(order2.cl_id, order2.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order2, bar1)
        self.assertTrue(handler.stop_limit_ready(order2.cl_id, order2.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order2, bar2)
        self.assertTrue(handler.stop_limit_ready(order2.cl_id, order2.cl_ord_id))
        self.assertEquals(18, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL
        order3 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="3", inst_id="1",
                                                      action=Sell, type=StopLimit,
                                                      qty=1000,
                                                      limit_price=20,
                                                      stop_price=18.5)
        fill_info = handler.process_w_price_qty(order3, 19, 1000)
        self.assertFalse(handler.stop_limit_ready(order3.cl_id, order3.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order3, 18, 1000)
        self.assertTrue(handler.stop_limit_ready(order3.cl_id, order3.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order3, 20, 1000)
        self.assertTrue(handler.stop_limit_ready(order3.cl_id, order3.cl_ord_id))
        self.assertEquals(20, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL with bar
        order4 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="4", inst_id="1",
                                                      action=Sell, type=StopLimit,
                                                      qty=1000,
                                                      limit_price=20,
                                                      stop_price=18.5)
        fill_info = handler.process(order4, bar1)
        self.assertFalse(handler.stop_limit_ready(order4.cl_id, order4.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order4, bar2)
        self.assertTrue(handler.stop_limit_ready(order4.cl_id, order4.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order4, bar1)
        self.assertTrue(handler.stop_limit_ready(order4.cl_id, order4.cl_ord_id))
        self.assertEquals(20, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

    def test_trailing_stop_order_handler(self):
        handler = TrailingStopOrderHandler(self.config)

        bar1 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=16, high=18, low=15, close=17, volume=1000)
        bar2 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=17, high=19, low=16, close=18, volume=1000)
        bar3 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=18, high=20, low=17, close=19, volume=1000)
        bar4 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=19, high=21, low=18, close=20, volume=1000)
        bar5 = ModelFactory.build_bar(timestamp=0, inst_id="1", open=20, high=22, low=19, close=21, volume=1000)

        # BUY with bar
        order1 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="1", inst_id="1", action=Buy,
                                                      type=TrailingStop,
                                                      qty=1000,
                                                      stop_price=5)

        self.assertEquals(0, handler.trailing_stop_exec_price(order1.cl_id, order1.cl_ord_id))

        fill_info = handler.process(order1, bar2)
        self.assertEquals(21, handler.trailing_stop_exec_price(order1.cl_id, order1.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order1, bar3)
        self.assertEquals(21, handler.trailing_stop_exec_price(order1.cl_id, order1.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order1, bar1)
        self.assertEquals(20, handler.trailing_stop_exec_price(order1.cl_id, order1.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order1, bar3)
        self.assertEquals(20, handler.trailing_stop_exec_price(order1.cl_id, order1.cl_ord_id))
        self.assertEquals(20, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # BUY
        order2 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="2", inst_id="1", action=Buy,
                                                      type=TrailingStop,
                                                      qty=1000,
                                                      stop_price=5)

        self.assertEquals(0, handler.trailing_stop_exec_price(order2.cl_id, order2.cl_ord_id))

        fill_info = handler.process_w_price_qty(order2, 16, 1000)
        self.assertEquals(21, handler.trailing_stop_exec_price(order2.cl_id, order2.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order2, 17, 1000)
        self.assertEquals(21, handler.trailing_stop_exec_price(order2.cl_id, order2.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order2, 15, 1000)
        self.assertEquals(20, handler.trailing_stop_exec_price(order2.cl_id, order2.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order2, 19, 1000)
        self.assertEquals(20, handler.trailing_stop_exec_price(order2.cl_id, order2.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order2, 20, 1000)
        self.assertEquals(20, handler.trailing_stop_exec_price(order2.cl_id, order2.cl_ord_id))
        self.assertEquals(20, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL with bar
        order3 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="3", inst_id="1",
                                                      action=Sell,
                                                      type=TrailingStop, qty=1000,
                                                      stop_price=5)

        self.assertEquals(0, handler.trailing_stop_exec_price(order3.cl_id, order3.cl_ord_id))

        fill_info = handler.process(order3, bar4)
        self.assertEquals(16, handler.trailing_stop_exec_price(order3.cl_id, order3.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order3, bar3)
        self.assertEquals(16, handler.trailing_stop_exec_price(order3.cl_id, order3.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order3, bar5)
        self.assertEquals(17, handler.trailing_stop_exec_price(order3.cl_id, order3.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process(order3, bar3)
        self.assertEquals(17, handler.trailing_stop_exec_price(order3.cl_id, order3.cl_ord_id))
        self.assertEquals(17, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)

        # SELL
        order4 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="4", inst_id="1",
                                                      action=Sell,
                                                      type=TrailingStop, qty=1000,
                                                      stop_price=5)

        self.assertEquals(0, handler.trailing_stop_exec_price(order4.cl_id, order4.cl_ord_id))

        fill_info = handler.process_w_price_qty(order4, 21, 1000)
        self.assertEquals(16, handler.trailing_stop_exec_price(order4.cl_id, order4.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order4, 20, 1000)
        self.assertEquals(16, handler.trailing_stop_exec_price(order4.cl_id, order4.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order4, 22, 1000)
        self.assertEquals(17, handler.trailing_stop_exec_price(order4.cl_id, order4.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order4, 18, 1000)
        self.assertEquals(17, handler.trailing_stop_exec_price(order4.cl_id, order4.cl_ord_id))
        self.assertEquals(None, fill_info)

        fill_info = handler.process_w_price_qty(order4, 17, 1000)
        self.assertEquals(17, handler.trailing_stop_exec_price(order4.cl_id, order4.cl_ord_id))
        self.assertEquals(17, fill_info.fill_price)
        self.assertEquals(1000, fill_info.fill_qty)
