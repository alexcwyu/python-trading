from unittest import TestCase

from pymongo import MongoClient

from algotrader.model.sample_factory import *


class PersistenceTest(TestCase):
    host = "localhost"
    port = 27017
    dbname = "test"
    client = None
    db = None

    @classmethod
    def setUpClass(cls):
        cls.client = MongoClient(host=cls.host, port=cls.port)
        cls.db = cls.client[cls.dbname]

        cls.tests = cls.db['tests']
        cls.factory = SampleFactory()

    @classmethod
    def tearDownClass(cls):
        cls.client.drop_database(cls.dbname)

    def setUp(self):
        pass

    def tearDown(self):
        PersistenceTest.tests.remove()

    def test_bar(self):
        inst = PersistenceTest.factory.sample_instrument()
        self.__test_persistence(Instrument, inst)

    def test_underlying(self):
        underlying = self.factory.sample_underlying()
        self.__test_persistence(Underlying, underlying)

    def test_derivative_traits(self):
        derivative_traits = self.factory.sample_derivative_traits()
        self.__test_persistence(DrivativeTraits, derivative_traits)

    def test_asset(self):
        asset = self.factory.sample_asset()
        self.__test_persistence(Underlying.Asset, asset)

    def test_exchange(self):
        exchange = self.factory.sample_exchange()
        self.__test_persistence(Exchange, exchange)

    def test_currency(self):
        currency = self.factory.sample_currency()
        self.__test_persistence(Currency, currency)

    def test_country(self):
        country = self.factory.sample_country()
        self.__test_persistence(Country, country)

    def test_holiday(self):
        holiday = self.factory.sample_holiday()
        self.__test_persistence(HolidaySeries.Holiday, holiday)

    def test_trading_holidays(self):
        trading_holiday = self.factory.sample_trading_holidays()
        self.__test_persistence(HolidaySeries, trading_holiday)

    def test_trading_session(self):
        session = self.factory.sample_trading_session()
        self.__test_persistence(TradingHours.Session, session)

    def test_trading_hours(self):
        trading_hours = self.factory.sample_trading_hours()
        self.__test_persistence(TradingHours, trading_hours)

    def test_timezone(self):
        timezone = self.factory.sample_timezone()
        self.__test_persistence(TimeZone, timezone)

    def test_data_series_item(self):
        item = self.factory.sample_data_series_item()
        self.__test_persistence(DataSeries.Item, item)

    def test_data_series(self):
        ds = self.factory.sample_data_series()
        self.__test_persistence(DataSeries, ds)

    def test_bar(self):
        self.__test_persistence(Bar, self.factory.sample_bar())

    def test_quote(self):
        self.__test_persistence(Quote, self.factory.sample_quote())

    def test_trade(self):
        self.__test_persistence(Trade, self.factory.sample_trade())

    def test_market_depth(self):
        self.__test_persistence(MarketDepth, self.factory.sample_market_depth())

    def test_new_order_request(self):
        self.__test_persistence(NewOrderRequest, self.factory.sample_new_order_request())

    def test_order_replace_request(self):
        self.__test_persistence(OrderReplaceRequest, self.factory.sample_order_replace_request())

    def test_order_cancel_request(self):
        self.__test_persistence(OrderCancelRequest, self.factory.sample_order_cancel_request())

    def test_order_status_update(self):
        self.__test_persistence(OrderStatusUpdate, self.factory.sample_order_status_update())

    def test_execution_report(self):
        self.__test_persistence(ExecutionReport, self.factory.sample_execution_report())

    def test_account_value(self):
        self.__test_persistence(AccountValue, self.factory.sample_account_value())

    def test_account_update(self):
        self.__test_persistence(AccountUpdate, self.factory.sample_account_update())

    def test_portfolio_update(self):
        self.__test_persistence(PortfolioUpdate, self.factory.sample_portfolio_update())

    def test_account(self):
        self.__test_persistence(Account, self.factory.sample_account())

    def test_portfolio(self):
        self.__test_persistence(Portfolio, self.factory.sample_portfolio())

    def test_performance(self):
        self.__test_persistence(Performance, self.factory.sample_performance())

    def test_pnl(self):
        self.__test_persistence(Pnl, self.factory.sample_pnl())

    def test_drawdown(self):
        self.__test_persistence(DrawDown, self.factory.sample_drawdown())

    def test_config(self):
        self.__test_persistence(Config, self.factory.sample_config())

    def test_strategy(self):
        self.__test_persistence(Strategy, self.factory.sample_strategy())

    def test_order(self):
        self.__test_persistence(Order, self.factory.sample_order())

    def test_position(self):
        self.__test_persistence(Position, self.factory.sample_position())

    def test_client_order_id(self):
        self.__test_persistence(ClientOrderId, self.factory.sample_client_order_id())

    def __test_persistence(self, cls, obj):
        data = protobuf_to_dict(obj)
        PersistenceTest.tests.update({'_id': 1}, data, upsert=True)
        result = PersistenceTest.tests.find_one({"_id": 1})
        del result['_id']
        new_obj = dict_to_protobuf(cls, result)
        self.assertEqual(obj, new_obj)
