import datetime
from unittest import TestCase

from nose_parameterized import parameterized, param

from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed
from algotrader.config.trading import BacktestingConfig
from algotrader.event.account import AccountUpdate, PortfolioUpdate
from algotrader.event.market_data import Bar, Trade, Quote, MarketDepth, MDOperation, MDSide
from algotrader.event.market_data import BarSize, BarType
from algotrader.event.order import NewOrderRequest, OrderCancelRequest, OrderReplaceRequest, OrderStatusUpdate, \
    ExecutionReport, TIF, \
    OrdStatus, OrdAction, OrdType
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.feed.pandas_memory import PandasMemoryDataFeed
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.technical.ma import SMA
from algotrader.trading.account import Account
from algotrader.trading.order import Order
from algotrader.trading.position import Position
from algotrader.trading.ref_data import Instrument, Exchange, Currency
from algotrader.utils.ser_deser import MsgPackSerializer, JsonSerializer, MapSerializer
from algotrader.utils.time_series import DataSeries

from algotrader.config.app import ApplicationConfig
from algotrader.trading.context import ApplicationContext

params = [
    param('MsgPackSerializer', MsgPackSerializer),
    param('JsonSerializer', JsonSerializer),
    param('MapSerializer', MapSerializer)
]


class SerializerTest(TestCase):
    # Market Data Event
    @parameterized.expand(params)
    def test_bar(self, name, serializer):
        item = Bar(open=18, high=19, low=17, close=17.5, vol=100, inst_id=1, timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_quote(self, name, serializer):
        item = Quote(bid=18, ask=19, bid_size=200, ask_size=500, inst_id=1, timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_trade(self, name, serializer):
        item = Trade(price=20, size=200, inst_id=1, timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_market_depth(self, name, serializer):
        item = MarketDepth(inst_id=1, timestamp=datetime.datetime.now(), provider_id=20, position=10,
                           operation=MDOperation.Insert, side=MDSide.Ask,
                           price=10.1, size=20)
        SerializerTest.ser_deser(name, serializer, item)

    # Order Event
    @parameterized.expand(params)
    def test_new_order_request(self, name, serializer):
        item = NewOrderRequest(timestamp=datetime.datetime.now(), cl_id=1, cl_ord_id=2, portf_id=3, broker_id='IB',
                               inst_id=3,
                               action=OrdAction.BUY, type=OrdType.LIMIT,
                               qty=10, limit_price=16.01,
                               stop_price=17.5, tif=TIF.DAY, oca_tag="WTF", params=None)
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_order_replace_request(self, name, serializer):
        item = OrderReplaceRequest(timestamp=datetime.datetime.now(), cl_id=1, cl_ord_id=1, type=OrdType.LIMIT,
                                   qty=12, limit_price=13.2, stop_price=13.5, tif=TIF.DAY, oca_tag="WTF", params=None)
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_order_cancel_request(self, name, serializer):
        item = OrderCancelRequest(timestamp=datetime.datetime.now(), cl_id=1, cl_ord_id=1, params=None)
        SerializerTest.ser_deser(name, serializer, item)

    # Execution Event
    @parameterized.expand(params)
    def test_order_status_update(self, name, serializer):
        item = OrderStatusUpdate(broker_id="IB", ord_id=1, cl_id=1, cl_ord_id=1, inst_id=3,
                                 timestamp=datetime.datetime.now(),
                                 filled_qty=10,
                                 avg_price=15.6, status=OrdStatus.NEW)
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_execution_report(self, name, serializer):
        item = ExecutionReport(broker_id="IB", ord_id=1, cl_id=1, cl_ord_id=1, inst_id=3,
                               timestamp=datetime.datetime.now(),
                               er_id=None,
                               last_qty=10, last_price=10.8,
                               filled_qty=140, avg_price=21.2, commission=18,
                               status=OrdStatus.NEW)
        SerializerTest.ser_deser(name, serializer, item)

    # Account Event
    @parameterized.expand(params)
    def test_account_update(self, name, serializer):
        item = AccountUpdate("TEST", "Pnl", "USD", 286.8, timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_portfolio_update(self, name, serializer):
        item = PortfolioUpdate(4, 100, 26.1, 2610, 24, 210.0, 0.0,
                               "TEST", timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(name, serializer, item)

    # Ref Data
    @parameterized.expand(params)
    def test_instrument(self, name, serializer):
        item = Instrument(3, "Google", "STK", "GOOG", "SMART", "USD", alt_symbol={"IB": "GOOG"}, alt_exch_id=None,
                          sector=None, group=None,
                          put_call=None, expiry_date=None, und_inst_id=None, factor=1, strike=0.0, margin=0.0)
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_exchange(self, name, serializer):
        item = Exchange("SEHK", "SEHK")
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_currency(self, name, serializer):
        item = Currency("USD", "US Dollar")
        SerializerTest.ser_deser(name, serializer, item)

    # Trade Data

    @parameterized.expand(params)
    def test_position(self, name, serializer):
        item = Position(inst_id=1)
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_order(self, name, serializer):
        nos = NewOrderRequest(timestamp=None, cl_id=None, cl_ord_id=None, portf_id=None, broker_id=None, inst_id=None,
                              action=None, type=None,
                              qty=0, limit_price=0,
                              stop_price=0, tif=TIF.DAY, oca_tag=None, params=None)

        item = Order(nos=nos)
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_account(self, id, serializer):
        item = Account(acct_id="")

        SerializerTest.ser_deser(id, serializer, item)

    @parameterized.expand(params)
    def test_data_series(self, name, serializer):
        item = DataSeries("close", missing_value=0)

        t = datetime.datetime(2000, 1, 1, 11, 34, 59)

        values = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
                  45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]
        for idx, value in enumerate(values):
            item.add({"timestamp": t, "v1": value, "v2": value})
            t = t + datetime.timedelta(0, 3)

        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_indicator(self, name, serializer):
        self.app_context = ApplicationContext()

        bar = self.app_context.inst_data_mgr.get_series("bar")
        sma = SMA(bar.name, 'close', 1, missing_value=0)
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)
        t3 = t2 + datetime.timedelta(0, 3)

        bar.add({"timestamp": t1, "close": 2.0, "open": 0})
        bar.add({"timestamp": t2, "close": 2.4, "open": 1.4})

        bar.add({"timestamp": t3, "close": 2.8, "open": 1.8})

        SerializerTest.ser_deser(name, serializer, sma)

    @parameterized.expand(params)
    def test_trading_config(self, name, serializer):
        instrument = 0

        dates = [datetime.datetime(2000, 1, 1), datetime.datetime(2015, 1, 1)]

        config = BacktestingConfig(stg_id="sma", portfolio_id='test',
                                   instrument_ids=[instrument],
                                   subscription_types=[BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                                   from_date=dates[0], to_date=dates[-1],
                                   broker_id=Broker.Simulator,
                                   feed_id=Feed.PandasMemory)
        SerializerTest.ser_deser(name, serializer, config)

    # # TODO fix error
    # @parameterized.expand(params)
    # def test_portfolio(self, name, serializer):
    #     item = Portfolio(portf_id="", cash=1000)
    #     SerializerTest.ser_deser(name, serializer, item)
    #
    #
    # # TODO fix json error
    # @parameterized.expand(params)
    # def test_strategy(self, name, serializer):
    #     stg = Strategy(stg_id='st1', next_ord_id=0, trading_config=None, ref_data_mgr=None)
    #     nos = NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
    #                     limit_price=18.5)
    #
    #     order = Order(nos=nos)
    #
    #     stg.ord_req[nos.cl_ord_id] = nos
    #     stg.order[order.cl_ord_id] = order
    #     stg.add_position(nos.inst_id, nos.cl_id, nos.cl_ord_id, nos.qty)
    #     stg.update_position_price(time=0, inst_id=nos.inst_id, price=100)
    #
    #     SerializerTest.ser_deser(name, serializer, stg)



    @staticmethod
    def ser_deser(name, serializer, item):
        packed = serializer.serialize(item)
        unpacked = serializer.deserialize(packed)
        print "===== %s" % name
        print packed
        print item
        print unpacked
        print MapSerializer.extract_slot(item)
        print MapSerializer.extract_slot(unpacked)
        assert MapSerializer.extract_slot(item) == MapSerializer.extract_slot(unpacked)
