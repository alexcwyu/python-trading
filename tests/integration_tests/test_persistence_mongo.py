from pymongo import MongoClient
from unittest import TestCase

from algotrader.utils.protobuf_to_dict import *
from tests.sample_factory import *


class MongoPersistenceTest(TestCase):
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
        MongoPersistenceTest.tests.remove()

    def test_instrument(self):
        inst = MongoPersistenceTest.factory.sample_instrument()
        self.__test_persistence(Instrument, inst)

    def test_exchange(self):
        exchange = self.factory.sample_exchange()
        self.__test_persistence(Exchange, exchange)

    def test_currency(self):
        currency = self.factory.sample_currency()
        self.__test_persistence(Currency, currency)

    def test_country(self):
        country = self.factory.sample_country()
        self.__test_persistence(Country, country)

    def test_trading_holidays(self):
        trading_holiday = self.factory.sample_trading_holidays()
        self.__test_persistence(HolidaySeries, trading_holiday)

    def test_trading_hours(self):
        trading_hours = self.factory.sample_trading_hours()
        self.__test_persistence(TradingHours, trading_hours)

    def test_timezone(self):
        timezone = self.factory.sample_timezone()
        self.__test_persistence(TimeZone, timezone)

    def test_time_series(self):
        ds = self.factory.sample_time_series()
        self.__test_persistence(TimeSeries, ds)

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

    def test_account_update(self):
        self.__test_persistence(AccountUpdate, self.factory.sample_account_update())

    def test_portfolio_update(self):
        self.__test_persistence(PortfolioUpdate, self.factory.sample_portfolio_update())

    def test_account_state(self):
        self.__test_persistence(AccountState, self.factory.sample_account_state())

    def test_portfolio_state(self):
        self.__test_persistence(PortfolioState, self.factory.sample_portfolio_state())

    def test_strategy_state(self):
        self.__test_persistence(StrategyState, self.factory.sample_strategy_state())

    def test_order_state(self):
        self.__test_persistence(OrderState, self.factory.sample_order_state())

    def test_sequence(self):
        self.__test_persistence(Sequence, self.factory.sample_sequence())

    def __test_persistence(self, cls, obj):
        data = protobuf_to_dict(obj)
        MongoPersistenceTest.tests.update({'_id': 1}, data, upsert=True)
        result = MongoPersistenceTest.tests.find_one({"_id": 1})
        del result['_id']
        new_obj = dict_to_protobuf(cls, result)
        self.assertEqual(obj, new_obj)
