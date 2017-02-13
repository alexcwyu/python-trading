from unittest import TestCase

from algotrader.model.sample_factory import *


class ModelFactoryTest(TestCase):
    def setUp(self):
        self.factory = SampleFactory()

    def test_instrument(self):
        inst = self.factory.sample_instrument()
        self.__test_serializaion(Instrument, inst)

    def test_underlying(self):
        underlying = self.factory.sample_underlying()
        self.__test_serializaion(Underlying, underlying)

    def test_derivative_traits(self):
        derivative_traits = self.factory.sample_derivative_traits()
        self.__test_serializaion(DrivativeTraits, derivative_traits)

    def test_asset(self):
        asset = self.factory.sample_asset()
        self.__test_serializaion(Underlying.Asset, asset)

    def test_exchange(self):
        exchange = self.factory.sample_exchange()
        self.__test_serializaion(Exchange, exchange)

    def test_currency(self):
        currency = self.factory.sample_currency()
        self.__test_serializaion(Currency, currency)

    def test_country(self):
        country = self.factory.sample_country()
        self.__test_serializaion(Country, country)

    def test_holiday(self):
        holiday = self.factory.sample_holiday()
        self.__test_serializaion(HolidaySeries.Holiday, holiday)

    def test_trading_holidays(self):
        trading_holiday = self.factory.sample_trading_holidays()
        self.__test_serializaion(HolidaySeries, trading_holiday)

    def test_trading_session(self):
        session = self.factory.sample_trading_session()
        self.__test_serializaion(TradingHours.Session, session)

    def test_trading_hours(self):
        trading_hours = self.factory.sample_trading_hours()
        self.__test_serializaion(TradingHours, trading_hours)

    def test_timezone(self):
        timezone = self.factory.sample_timezone()
        self.__test_serializaion(TimeZone, timezone)

    def test_time_series_item(self):
        item = self.factory.sample_time_series_item()
        self.__test_serializaion(TimeSeries.Item, item)

    def test_time_series(self):
        ds = self.factory.sample_time_series()
        self.__test_serializaion(TimeSeries, ds)

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

    def test_account_value(self):
        self.__test_serializaion(AccountValue, self.factory.sample_account_value())

    def test_account_update(self):
        self.__test_serializaion(AccountUpdate, self.factory.sample_account_update())

    def test_portfolio_update(self):
        self.__test_serializaion(PortfolioUpdate, self.factory.sample_portfolio_update())

    def test_account_state(self):
        self.__test_serializaion(AccountState, self.factory.sample_account_state())

    def test_portfolio_state(self):
        self.__test_serializaion(PortfolioState, self.factory.sample_portfolio_state())

    def test_performance(self):
        self.__test_serializaion(Performance, self.factory.sample_performance())

    def test_pnl(self):
        self.__test_serializaion(Pnl, self.factory.sample_pnl())

    def test_drawdown(self):
        self.__test_serializaion(DrawDown, self.factory.sample_drawdown())

    def test_config(self):
        self.__test_serializaion(Config, self.factory.sample_config())

    def test_strategy_state(self):
        self.__test_serializaion(StrategyState, self.factory.sample_strategy_state())

    def test_order_state(self):
        self.__test_serializaion(OrderState, self.factory.sample_order_state())

    def test_position(self):
        self.__test_serializaion(Position, self.factory.sample_position())

    def test_order_position(self):
        self.__test_serializaion(OrderPosition, self.factory.sample_order_position())

    def test_sequence(self):
        self.__test_serializaion(Sequence, self.factory.sample_sequence())

    def __test_serializaion(self, cls, obj):
        print(obj)

        obj2 = cls()
        obj2.ParseFromString(obj.SerializeToString())
        self.assertEqual(obj, obj2)

        obj3 = dict_to_protobuf(cls, protobuf_to_dict(obj))
        self.assertEqual(obj, obj3)
