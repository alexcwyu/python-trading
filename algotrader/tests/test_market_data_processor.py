from unittest import TestCase

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.event.order import Order, OrdAction, OrdType
from algotrader.provider.broker import SimConfig, BarProcessor, TradeProcessor, QuoteProcessor


class MarketDataProcessorTest(TestCase):
    def test_bar_processor(self):
        config = SimConfig()
        processor = BarProcessor()

        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        bar = Bar(open=18, high=19, low=17, close=17.5)

        self.assertEqual(17.5, processor.get_price(order, bar, config))
        self.assertEqual(1000, processor.get_qty(order, bar, config))

        config2 = SimConfig(fill_on_bar_mode=SimConfig.FillMode.NEXT_OPEN)
        self.assertEqual(18, processor.get_price(order, bar, config2))
        self.assertEqual(1000, processor.get_qty(order, bar, config2))

    def test_trader_processor(self):
        config = SimConfig()
        processor = TradeProcessor()

        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        trade = Trade(price=20, size=200)

        self.assertEqual(20, processor.get_price(order, trade, config))
        self.assertEqual(1000, processor.get_qty(order, trade, config))

    def test_quote_processor(self):
        config = SimConfig()
        processor = QuoteProcessor()

        order = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        quote = Quote(bid=18, ask=19, bid_size=200, ask_size=500)

        self.assertEqual(19, processor.get_price(order, quote, config))
        self.assertEqual(500, processor.get_qty(order, quote, config))

        order2 = Order(ord_id=2, instrument="HSI", action=OrdAction.SELL, type=OrdType.LIMIT, qty=1000,
                       limit_price=18.5)
        self.assertEqual(18, processor.get_price(order2, quote, config))
        self.assertEqual(200, processor.get_qty(order2, quote, config))
