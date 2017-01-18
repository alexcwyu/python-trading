from unittest import TestCase

from algotrader.model.model_helper import *
from algotrader.model.sample_factory import *


class ModelHelperTest(TestCase):
    factory = SampleFactory()

    def setUp(self):
        self.factory = SampleFactory()

    def test_instrument(self):
        inst = ModelHelperTest.factory.sample_instrument()
        self.assertEqual("2800.HK@SEHK", ModelHelper.get_id(inst))

    def test_exchange(self):
        exchange = self.factory.sample_exchange()
        self.assertEqual("SEHK", ModelHelper.get_id(exchange))

    def test_currency(self):
        currency = self.factory.sample_currency()
        self.assertEqual("HKD", ModelHelper.get_id(currency))

    def test_country(self):
        country = self.factory.sample_country()
        self.assertEqual("US", ModelHelper.get_id(country))

    def test_trading_holidays(self):
        self.assertEqual("HK holiday", ModelHelper.get_id(self.factory.sample_trading_holidays()))

    def test_trading_hours(self):
        self.assertEqual("SEHK_trdinghr", ModelHelper.get_id(self.factory.sample_trading_hours()))

    def test_timezone(self):
        self.assertEqual("Venezuela Standard Time", ModelHelper.get_id(self.factory.sample_timezone()))

    def test_time_series(self):
        self.assertEqual("HSI.BAR.86400", ModelHelper.get_id(self.factory.sample_time_series()))

    def test_bar(self):
        self.assertEqual("Bar.HSI@SEHK.0.86400.IB.12312", ModelHelper.get_id(self.factory.sample_bar()))

    def test_quote(self):
        self.assertEqual("Quote.HSI@SEHK.IB.12312", ModelHelper.get_id(self.factory.sample_quote()))

    def test_trade(self):
        self.assertEqual("Trade.HSI@SEHK.IB.12312", ModelHelper.get_id(self.factory.sample_trade()))

    def test_market_depth(self):
        self.assertEqual("MarketDepth.HSI@SEHK.IB.12312", ModelHelper.get_id(self.factory.sample_market_depth()))

    def test_new_order_request(self):
        self.assertEqual("BuyLowSellHigh.1", ModelHelper.get_id(self.factory.sample_new_order_request()))

    def test_order_replace_request(self):
        self.assertEqual("BuyLowSellHigh.1", ModelHelper.get_id(self.factory.sample_order_replace_request()))

    def test_order_cancel_request(self):
        self.assertEqual("BuyLowSellHigh.1", ModelHelper.get_id(self.factory.sample_order_cancel_request()))

    def test_order_status_update(self):
        self.assertEqual("IB.event_123", ModelHelper.get_id(self.factory.sample_order_status_update()))

    def test_execution_report(self):
        self.assertEqual("IB.event_123", ModelHelper.get_id(self.factory.sample_execution_report()))

    def test_account_update(self):
        self.assertEqual("IB.e_123", ModelHelper.get_id(self.factory.sample_account_update()))

    def test_portfolio_update(self):
        self.assertEqual("IB.e_456", ModelHelper.get_id(self.factory.sample_portfolio_update()))

    def test_account_state(self):
        self.assertEqual("test_acct", ModelHelper.get_id(self.factory.sample_account_state()))

    def test_portfolio_state(self):
        self.assertEqual("test_portf", ModelHelper.get_id(self.factory.sample_portfolio_state()))

    def test_strategy_state(self):
        self.assertEqual("BLSH", ModelHelper.get_id(self.factory.sample_strategy_state()))

    def test_order_state(self):
        self.assertEqual("BuyLowSellHigh.1", ModelHelper.get_id(self.factory.sample_order_state()))

    def test_config(self):
        self.assertEqual("testConfig", ModelHelper.get_id(self.factory.sample_config()))
