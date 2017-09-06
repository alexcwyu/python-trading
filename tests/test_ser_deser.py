from unittest import TestCase

from algotrader.model.market_data_pb2 import *
from algotrader.model.ref_data_pb2 import *
from algotrader.model.time_series_pb2 import *
from algotrader.model.time_series2_pb2 import Series
from algotrader.model.frame_pb2 import Frame
from algotrader.model.trade_data_pb2 import *
from algotrader.utils.protobuf_to_dict import *
from tests.sample_factory import SampleFactory


class SerializationTest(TestCase):
    def setUp(self):
        self.factory = SampleFactory()

    def test_instrument(self):
        inst = self.factory.sample_instrument()
        self.__test_serializaion(Instrument, inst)

    def test_exchange(self):
        exchange = self.factory.sample_exchange()
        self.__test_serializaion(Exchange, exchange)

    def test_currency(self):
        currency = self.factory.sample_currency()
        self.__test_serializaion(Currency, currency)

    def test_country(self):
        country = self.factory.sample_country()
        self.__test_serializaion(Country, country)

    def test_trading_holidays(self):
        trading_holiday = self.factory.sample_trading_holidays()
        self.__test_serializaion(HolidaySeries, trading_holiday)

    def test_trading_hours(self):
        trading_hours = self.factory.sample_trading_hours()
        self.__test_serializaion(TradingHours, trading_hours)

    def test_timezone(self):
        timezone = self.factory.sample_timezone()
        self.__test_serializaion(TimeZone, timezone)

    def test_series(self):
        ds = self.factory.sample_series()
        self.__test_serializaion(Series, ds)

    def test_frame(self):
        f = self.factory.sample_frame()
        self.__test_serializaion(Frame, f)

    def test_bar(self):
        self.__test_serializaion(Bar, self.factory.sample_bar())

    def test_quote(self):
        self.__test_serializaion(Quote, self.factory.sample_quote())

    def test_trade(self):
        self.__test_serializaion(Trade, self.factory.sample_trade())

    def test_market_depth(self):
        self.__test_serializaion(MarketDepth, self.factory.sample_market_depth())

    def test_new_order_request(self):
        self.__test_serializaion(NewOrderRequest, self.factory.sample_new_order_request())

    def test_order_replace_request(self):
        self.__test_serializaion(OrderReplaceRequest, self.factory.sample_order_replace_request())

    def test_order_cancel_request(self):
        self.__test_serializaion(OrderCancelRequest, self.factory.sample_order_cancel_request())

    def test_order_status_update(self):
        self.__test_serializaion(OrderStatusUpdate, self.factory.sample_order_status_update())

    def test_execution_report(self):
        self.__test_serializaion(ExecutionReport, self.factory.sample_execution_report())

    def test_account_update(self):
        self.__test_serializaion(AccountUpdate, self.factory.sample_account_update())

    def test_portfolio_update(self):
        self.__test_serializaion(PortfolioUpdate, self.factory.sample_portfolio_update())

    def test_account_state(self):
        self.__test_serializaion(AccountState, self.factory.sample_account_state())

    def test_portfolio_state(self):
        self.__test_serializaion(PortfolioState, self.factory.sample_portfolio_state())

    def test_strategy_state(self):
        self.__test_serializaion(StrategyState, self.factory.sample_strategy_state())

    def test_order_state(self):
        self.__test_serializaion(OrderState, self.factory.sample_order_state())

    def test_sequence(self):
        self.__test_serializaion(Sequence, self.factory.sample_sequence())

    def __test_serializaion(self, cls, obj):
        #print(obj)

        obj2 = cls()
        obj2.ParseFromString(obj.SerializeToString())
        self.assertEqual(obj, obj2)

        obj3 = dict_to_protobuf(cls, protobuf_to_dict(obj))
        self.assertEqual(obj, obj3)
