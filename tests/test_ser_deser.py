import datetime
from unittest import TestCase

from nose_parameterized import parameterized, param

from algotrader.event.account import AccountUpdate, PortfolioUpdate
from algotrader.event.market_data import Bar, Trade, Quote, MarketDepth, MDOperation, MDSide
from algotrader.event.order import NewOrderRequest, OrderCancelRequest, OrderReplaceRequest, OrderStatusUpdate, ExecutionReport, TIF, \
    OrdStatus, OrdAction, OrdType
from algotrader.strategy.strategy import Strategy
from algotrader.trading.account import Account
from algotrader.trading.order import Order
from algotrader.trading.portfolio import Portfolio
from algotrader.trading.position import Position
from algotrader.trading.ref_data import Instrument, Exchange, Currency
from algotrader.utils.ser_deser import MsgPackSerializer, JsonSerializer
from algotrader.utils.time_series import DataSeries
from algotrader.technical import Indicator
from algotrader.technical.ma import SMA
from algotrader.trading.config import BacktestingConfig


params = [
    param(MsgPackSerializer()),
    param(JsonSerializer())
]


class SerializerTest(TestCase):
    # Market Data Event
    @parameterized.expand(params)
    def test_bar(self, serializer):
        item = Bar(open=18, high=19, low=17, close=17.5, vol=100, inst_id=1, timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_quote(self, serializer):
        item = Quote(bid=18, ask=19, bid_size=200, ask_size=500, inst_id=1, timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_trade(self, serializer):
        item = Trade(price=20, size=200, inst_id=1, timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_market_depth(self, serializer):
        item = MarketDepth(inst_id=1, timestamp=datetime.datetime.now(), provider_id=20, position=10,
                           operation=MDOperation.Insert, side=MDSide.Ask,
                           price=10.1, size=20)
        SerializerTest.ser_deser(serializer, item)

    # Order Event
    @parameterized.expand(params)
    def test_new_order_request(self, serializer):
        item = NewOrderRequest(timestamp=datetime.datetime.now(), cl_id=1, cl_ord_id=2, portf_id=3, broker_id='IB',
                               inst_id=3,
                               action=OrdAction.BUY, type=OrdType.LIMIT,
                               qty=10, limit_price=16.01,
                               stop_price=17.5, tif=TIF.DAY, oca_tag="WTF", params=None)
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_order_replace_request(self, serializer):
        item = OrderReplaceRequest(timestamp=datetime.datetime.now(), cl_id=1, cl_ord_id=1, type=OrdType.LIMIT,
                                   qty=12, limit_price=13.2, stop_price=13.5, tif=TIF.DAY, oca_tag="WTF", params=None)
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_order_cancel_request(self, serializer):
        item = OrderCancelRequest(timestamp=datetime.datetime.now(), cl_id=1, cl_ord_id=1, params=None)
        SerializerTest.ser_deser(serializer, item)

    # Execution Event
    @parameterized.expand(params)
    def test_order_status_update(self, serializer):
        item = OrderStatusUpdate(broker_id="IB", ord_id=1, cl_id=1, cl_ord_id=1, inst_id=3,
                                 timestamp=datetime.datetime.now(),
                                 filled_qty=10,
                                 avg_price=15.6, status=OrdStatus.NEW)
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_execution_report(self, serializer):
        item = ExecutionReport(broker_id="IB", ord_id=1, cl_id=1, cl_ord_id=1, inst_id=3,
                               timestamp=datetime.datetime.now(),
                               er_id=None,
                               last_qty=10, last_price=10.8,
                               filled_qty=140, avg_price=21.2, commission=18,
                               status=OrdStatus.NEW)
        SerializerTest.ser_deser(serializer, item)

    # Account Event
    @parameterized.expand(params)
    def test_account_update(self, serializer):
        item = AccountUpdate("TEST", "Pnl", "USD", 286.8, timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_portfolio_update(self, serializer):
        item = PortfolioUpdate(4, 100, 26.1, 2610, 24, 210.0, 0.0,
                               "TEST", timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(serializer, item)

    # Ref Data
    @parameterized.expand(params)
    def test_instrument(self, serializer):
        item = Instrument(3, "Google", "STK", "GOOG", "SMART", "USD", alt_symbol={"IB": "GOOG"}, alt_exch_id=None,
                          sector=None, group=None,
                          put_call=None, expiry_date=None, und_inst_id=None, factor=1, strike=0.0, margin=0.0)
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_exchange(self, serializer):
        item = Exchange("SEHK", "SEHK")
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_currency(self, serializer):
        item = Currency("USD", "US Dollar")
        SerializerTest.ser_deser(serializer, item)

    # Trade Data

    @parameterized.expand(params)
    def test_position(self, serializer):
        item = Position(inst_id=1)
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_order(self, serializer):
        nos = NewOrderRequest(timestamp=None, cl_id=None, cl_ord_id=None, portf_id=None, broker_id=None, inst_id=None,
                              action=None, type=None,
                              qty=0, limit_price=0,
                              stop_price=0, tif=TIF.DAY, oca_tag=None, params=None)

        item = Order(nos=nos)
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_account(self, serializer):
        item = Account(name="")

        SerializerTest.ser_deser(serializer, item)

    #TODO
    # @parameterized.expand(params)
    # def test_portfolio(self, serializer):
    #     item = Portfolio(portf_id="", cash=1000)
    #     SerializerTest.ser_deser(serializer, item)
    #

    #TODO
    # @parameterized.expand(params)
    # def test_strategy(self, serializer):
    #     item = Strategy("ST1", portfolio=None, instruments=[1, 12],
    #                     trading_config=None, ref_data_mgr=None, next_ord_id=0)
    #     SerializerTest.ser_deser(serializer, item)

    #TODO
    @parameterized.expand(params)
    def test_data_series(self, serializer):
        item = DataSeries()
        SerializerTest.ser_deser(serializer, item)

    #TODO
    @parameterized.expand(params)
    def test_indicator(self, serializer):
        item = SMA()
        SerializerTest.ser_deser(serializer, item)

    #TODO
    # @parameterized.expand(params)
    # def test_trading_config(self, serializer):
    #     item = BacktestingConfig()
    #     SerializerTest.ser_deser(serializer, item)



    @staticmethod
    def ser_deser(serializer, item):
        packed = serializer.serialize(item)
        unpacked = serializer.deserialize(packed)
        print item
        print unpacked
        assert item.__data__() == unpacked.__data__()
