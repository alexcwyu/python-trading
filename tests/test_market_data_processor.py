from unittest import TestCase

from algotrader.model.model_factory import ModelFactory
from algotrader.model.trade_data_pb2 import *
from algotrader.provider.broker.sim.data_processor import BarProcessor, TradeProcessor, QuoteProcessor
from algotrader.provider.broker.sim.sim_config import SimConfig


class MarketDataProcessorTest(TestCase):
    def test_bar_processor(self):
        config = SimConfig()
        processor = BarProcessor()

        order = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="1", inst_id="1", action=Buy,
                                                     type=Limit,
                                                     qty=1000, limit_price=18.5)
        bar = ModelFactory.build_bar(timestamp=0, inst_id="1", open=18, high=19, low=17, close=17.5, vol=1000)

        self.assertEqual(17.5, processor.get_price(order, bar, config))
        self.assertEqual(1000, processor.get_qty(order, bar, config))

        config2 = SimConfig(fill_on_bar_mode=SimConfig.FillMode.NEXT_OPEN)
        self.assertEqual(18, processor.get_price(order, bar, config2))
        self.assertEqual(1000, processor.get_qty(order, bar, config2))

    def test_trader_processor(self):
        config = SimConfig()
        processor = TradeProcessor()

        order = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="1", inst_id="1", action=Buy,
                                                     type=Limit,
                                                     qty=1000, limit_price=18.5)
        trade = ModelFactory.build_trade(timestamp=0, inst_id="1", price=20, size=200)

        self.assertEqual(20, processor.get_price(order, trade, config))
        self.assertEqual(200, processor.get_qty(order, trade, config))

    def test_quote_processor(self):
        config = SimConfig()
        processor = QuoteProcessor()

        order = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="1", inst_id="1", action=Buy,
                                                     type=Limit,
                                                     qty=1000, limit_price=18.5)
        quote = ModelFactory.build_quote(timestamp=0, inst_id="1", bid=18, ask=19, bid_size=200, ask_size=500)

        self.assertEqual(19, processor.get_price(order, quote, config))
        self.assertEqual(500, processor.get_qty(order, quote, config))

        order2 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id="2", inst_id="1",
                                                      action=Sell, type=Limit,
                                                      qty=1000,
                                                      limit_price=18.5)
        self.assertEqual(18, processor.get_price(order2, quote, config))
        self.assertEqual(200, processor.get_qty(order2, quote, config))
