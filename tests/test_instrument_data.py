from unittest import TestCase

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.trading.instrument_data import InstrumentDataManager


class InstrumentDataTest(TestCase):
    def setUp(self):
        self.inst_data_mgr = InstrumentDataManager()

    def test_get_bar(self):
        bar = self.inst_data_mgr.get_bar(1)
        self.assertIsNone(bar)

        bar1 = Bar(inst_id=1, open=20, high=21, low=19, close=20.5)
        self.inst_data_mgr.on_bar(bar1)
        bar = self.inst_data_mgr.get_bar(1)
        self.assertEqual(bar1, bar)

    def test_get_quote(self):
        quote = self.inst_data_mgr.get_quote(1)
        self.assertIsNone(quote)

        quote1 = Quote(inst_id=1, bid=18, ask=19, bid_size=200, ask_size=500)
        self.inst_data_mgr.on_quote(quote1)
        quote = self.inst_data_mgr.get_quote(1)
        self.assertEqual(quote1, quote)

    def test_get_trade(self):
        trade = self.inst_data_mgr.get_trade(1)
        self.assertIsNone(trade)

        trade1 = Trade(inst_id=1, price=20, size=200)
        self.inst_data_mgr.on_trade(trade1)
        trade = self.inst_data_mgr.get_trade(1)
        self.assertEqual(trade1, trade)

    def get_latest_price(self):
        price = self.inst_data_mgr.get_latest_price(1)
        self.assertIsNone(price)

        bar1 = Bar(inst_id=1, open=20, high=21, low=19, close=20.5)
        self.inst_data_mgr.on_bar(bar1)
        price = self.inst_data_mgr.get_latest_price(1)
        self.assertEqual(20.5, price)

        bar1 = Bar(inst_id=1, open=20, high=21, low=19, close=20.5, adj_close=22)
        self.inst_data_mgr.on_bar(bar1)
        price = self.inst_data_mgr.get_latest_price(1)
        self.assertEqual(22, price)

        quote1 = Quote(inst_id=1, bid=18, ask=19, bid_size=200, ask_size=500)
        self.inst_data_mgr.on_quote(quote1)
        price = self.inst_data_mgr.get_latest_price(1)
        self.assertEqual(18.5, price)

        trade1 = Trade(inst_id=1, price=20, size=200)
        self.inst_data_mgr.on_bar(trade1)
        price = self.inst_data_mgr.get_latest_price(1)
        self.assertEqual(20, price)
