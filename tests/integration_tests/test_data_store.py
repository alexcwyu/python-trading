from datetime import date, timedelta, datetime

from algotrader.config.app import ApplicationConfig, BacktestingConfig
from algotrader.config.persistence import MongoDBConfig, CassandraConfig, PersistenceConfig, InMemoryStoreConfig
from algotrader.event.account import AccountUpdate, PortfolioUpdate
from algotrader.event.market_data import Bar, Trade, Quote, MarketDepth, MDOperation, MDSide
from algotrader.event.market_data import BarSize, BarType
from algotrader.event.order import NewOrderRequest, OrderCancelRequest, OrderReplaceRequest, OrderStatusUpdate, \
    ExecutionReport, TIF, \
    OrdStatus, OrdAction, OrdType
from cassandra.cluster import Cluster
from nose_parameterized import parameterized, param
from unittest import TestCase

from algotrader.provider.broker import Broker
from algotrader.provider.datastore import DataStore
from algotrader.provider.datastore import PersistenceMode
from algotrader.provider.feed import Feed
from algotrader.strategy import Strategy
from algotrader.technical.ma import SMA
from algotrader.trading.account import Account
from algotrader.trading.clock import Clock
from algotrader.trading.context import ApplicationContext
from algotrader.trading.order import Order
from algotrader.trading.ref_data import Instrument, Exchange, Currency
from algotrader.trading.subscription import BarSubscriptionType
from algotrader.trading.subscription import HistDataSubscriptionKey, QuoteSubscriptionType, TradeSubscriptionType, \
    MarketDepthSubscriptionType
from algotrader.utils.date import date_to_unixtimemillis
from poc.ser_deser import MapSerializer

print
Cluster.port

persistence_config = PersistenceConfig(None,
                                       DataStore.Mongo, PersistenceMode.Batch,
                                       DataStore.Mongo, PersistenceMode.Batch,
                                       DataStore.Mongo, PersistenceMode.Batch,
                                       DataStore.Mongo, PersistenceMode.Batch)

# name = "test_%s" % int(time.time() * 1000)
name = "test"
create_at_start = True
cass_delete_at_stop = False
mongo_delete_at_stop = True
im_memory_delete_at_stop = True

app_config = ApplicationConfig(None, None, Clock.RealTime, persistence_config,
                               provider_configs=[MongoDBConfig(dbname=name, create_at_start=create_at_start,
                                                               delete_at_stop=mongo_delete_at_stop),
                                                 CassandraConfig(contact_points=['127.0.0.1'], keyspace=name,
                                                                 create_at_start=create_at_start,
                                                                 delete_at_stop=cass_delete_at_stop),
                                                 InMemoryStoreConfig(file="%s_db.p" % name,
                                                                     create_at_start=create_at_start,
                                                                     delete_at_stop=im_memory_delete_at_stop)])
context = ApplicationContext(app_config=app_config)
clock = context.clock
mongo = context.provider_mgr.get(DataStore.Mongo)
cassandra = context.provider_mgr.get(DataStore.Cassandra)
inmemory = context.provider_mgr.get(DataStore.InMemory)

params = [
    param('Mongo', mongo),
    param('Cassandra', cassandra),
    param('InMemory', inmemory)
]


class DataStoreTest(TestCase):
    @classmethod
    def setUpClass(cls):
        mongo.start(app_context=context)
        cassandra.start(app_context=context)
        inmemory.start(app_context=context)

    @classmethod
    def tearDownClass(cls):
        mongo.stop()
        cassandra.stop()
        inmemory.stop()

    @parameterized.expand(params)
    def test_subscribe_bars(self, name, datastore):
        start_date = date(2011, 1, 1)
        end_date = date(2011, 1, 5)
        sub_key = HistDataSubscriptionKey(inst_id=10, provider_id=Broker.IB,
                                          subscription_type=BarSubscriptionType(bar_type=BarType.Time,
                                                                                bar_size=BarSize.D1),
                                          from_date=start_date, to_date=end_date)

        date_val = start_date

        expect_val = []
        for i in range(1, 5):
            persistable = Bar(timestamp=date_to_unixtimemillis(date_val), type=BarType.Time, size=BarSize.D1,
                              inst_id=10, open=18 + i, high=19 + i, low=17 + i, close=17.5 + i, vol=100)
            datastore.save_bar(persistable)
            expect_val.append(persistable)
            date_val = date_val + timedelta(days=1)

        actual_val = datastore.load_mktdata(sub_key)
        self.assertEqual(expect_val, actual_val)

    @parameterized.expand(params)
    def test_subscribe_quotes(self, name, datastore):
        start_date = date(2011, 1, 1)
        end_date = date(2011, 1, 5)
        sub_key = HistDataSubscriptionKey(inst_id=10, provider_id=Broker.IB,
                                          subscription_type=QuoteSubscriptionType(),
                                          from_date=start_date, to_date=end_date)

        date_val = start_date

        expect_val = []
        for i in range(1, 5):
            persistable = Quote(timestamp=date_to_unixtimemillis(date_val), bid=18 + i, ask=19 + i,
                                bid_size=200, ask_size=500, inst_id=10)
            datastore.save_quote(persistable)
            expect_val.append(persistable)
            date_val = date_val + timedelta(days=1)

        actual_val = datastore.load_mktdata(sub_key)
        self.assertEqual(expect_val, actual_val)

    @parameterized.expand(params)
    def test_subscribe_trades(self, name, datastore):
        start_date = date(2011, 1, 1)
        end_date = date(2011, 1, 5)
        sub_key = HistDataSubscriptionKey(inst_id=10, provider_id=Broker.IB,
                                          subscription_type=TradeSubscriptionType(),
                                          from_date=start_date, to_date=end_date)

        date_val = start_date

        expect_val = []
        for i in range(1, 5):
            persistable = Trade(timestamp=date_to_unixtimemillis(date_val), price=20 + i, size=200 + i,
                                inst_id=10)
            datastore.save_trade(persistable)
            expect_val.append(persistable)
            date_val = date_val + timedelta(days=1)

        actual_val = datastore.load_mktdata(sub_key)
        self.assertEqual(expect_val, actual_val)

    @parameterized.expand(params)
    def test_subscribe_market_depths(self, name, datastore):
        start_date = date(2011, 1, 1)
        end_date = date(2011, 1, 5)
        sub_key = HistDataSubscriptionKey(inst_id=10, provider_id=Broker.IB,
                                          subscription_type=MarketDepthSubscriptionType(provider_id='20'),
                                          from_date=start_date, to_date=end_date)

        date_val = start_date

        expect_val = []
        for i in range(1, 5):
            persistable = MarketDepth(timestamp=date_to_unixtimemillis(date_val), inst_id=10,
                                      provider_id='20', position=10 + i,
                                      operation=MDOperation.Insert, side=MDSide.Ask,
                                      price=10.1 + i, size=20)
            datastore.save_market_depth(persistable)
            expect_val.append(persistable)
            date_val = date_val + timedelta(days=1)

        actual_val = datastore.load_mktdata(sub_key)
        self.assertEqual(expect_val, actual_val)

    @parameterized.expand(params)
    def test_multi_subscriptions(self, name, datastore):
        start_date = date(2011, 1, 1)
        end_date = date(2011, 1, 5)

        sub_key1 = HistDataSubscriptionKey(inst_id=99, provider_id=Broker.IB,
                                           subscription_type=BarSubscriptionType(bar_type=BarType.Time,
                                                                                 bar_size=BarSize.D1),
                                           from_date=start_date, to_date=end_date)

        sub_key2 = HistDataSubscriptionKey(inst_id=99, provider_id=Broker.IB,
                                           subscription_type=QuoteSubscriptionType(),
                                           from_date=start_date, to_date=end_date)

        sub_key3 = HistDataSubscriptionKey(inst_id=99, provider_id=Broker.IB,
                                           subscription_type=TradeSubscriptionType(),
                                           from_date=start_date, to_date=end_date)

        expect_val = []

        # out of range
        persistable = Bar(timestamp=date_to_unixtimemillis(date(2010, 12, 31)), type=BarType.Time,
                          size=BarSize.D1, inst_id=99, open=18, high=19, low=17, close=17.5, vol=100)
        datastore.save_bar(persistable)

        persistable = Bar(timestamp=date_to_unixtimemillis(date(2011, 1, 1)), type=BarType.Time,
                          size=BarSize.D1, inst_id=99, open=28, high=29, low=27, close=27.5, vol=100)
        datastore.save_bar(persistable)
        expect_val.append(persistable)

        persistable = Trade(timestamp=date_to_unixtimemillis(date(2011, 1, 2)), price=20, size=200,
                            inst_id=99)
        datastore.save_trade(persistable)
        expect_val.append(persistable)

        persistable = Trade(timestamp=date_to_unixtimemillis(date(2011, 1, 3)), price=30, size=200,
                            inst_id=99)
        datastore.save_trade(persistable)
        expect_val.append(persistable)

        # not same instrument
        persistable = Quote(timestamp=date_to_unixtimemillis(date(2011, 1, 3)), bid=18, ask=19, bid_size=200,
                            ask_size=500, inst_id=11)
        datastore.save_quote(persistable)

        persistable = Quote(timestamp=date_to_unixtimemillis(date(2011, 1, 4)), bid=18, ask=19, bid_size=200,
                            ask_size=500, inst_id=99)
        datastore.save_quote(persistable)
        expect_val.append(persistable)

        # out of range
        persistable = Quote(timestamp=date_to_unixtimemillis(date(2011, 1, 5)), bid=28, ask=29, bid_size=200,
                            ask_size=500, inst_id=99)
        datastore.save_quote(persistable)

        actual_val = datastore.load_mktdata(sub_key1, sub_key2, sub_key3)
        self.assertEqual(expect_val, actual_val)

    # Market Data Event

    @parameterized.expand(params)
    def test_bar(self, name, datastore):
        persistable = Bar(timestamp=clock.now(), open=18, high=19, low=17, close=17.5, vol=100, inst_id=999)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_bar, 'bars')

    @parameterized.expand(params)
    def test_quote(self, name, datastore):
        persistable = Quote(timestamp=clock.now(), bid=18, ask=19, bid_size=200, ask_size=500, inst_id=999)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_quote, 'quotes')

    @parameterized.expand(params)
    def test_trade(self, name, datastore):
        persistable = Trade(timestamp=clock.now(), price=20, size=200, inst_id=999)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_trade, 'trades')

    @parameterized.expand(params)
    def test_market_depth(self, name, datastore):
        persistable = MarketDepth(timestamp=clock.now(), inst_id=999, provider_id='20', position=10,
                                  operation=MDOperation.Insert, side=MDSide.Ask,
                                  price=10.1, size=20)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_market_depth, 'market_depths')

    # @parameterized.expand(params)
    # def test_data_series(self, name, datastore):
    #     item = DataSeries("close", missing_value=0)
    #
    #     t = datetime.datetime(2000, 1, 1, 11, 34, 59)
    #
    #     values = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
    #               45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]
    #     for idx, value in enumerate(values):
    #         item.add({"timestamp": t, "v1": value, "v2": value})
    #         t = t + datetime.timedelta(0, 3)
    #     DataStoreTest.save_load(name, item, datastore, datastore.save_time_series, 'time_series')

    @parameterized.expand(params)
    def test_indicator(self, name, datastore):
        self.app_context = ApplicationContext()

        bar = self.app_context.inst_data_mgr.get_series("bar")
        sma = SMA(bar.name, 'close', 1, missing_value=0)
        t1 = datetime.now()
        t2 = t1 + timedelta(0, 3)
        t3 = t2 + timedelta(0, 3)

        bar.add({"timestamp": t1, "close": 2.0, "open": 0})
        bar.add({"timestamp": t2, "close": 2.4, "open": 1.4})

        bar.add({"timestamp": t3, "close": 2.8, "open": 1.8})

        DataStoreTest.save_load(name, sma, datastore, datastore.save_time_series, 'time_series')

    # Order Event

    @parameterized.expand(params)
    def test_new_order_request(self, name, datastore):
        persistable = NewOrderRequest(timestamp=clock.now(), cl_id=1, cl_ord_id=2, portf_id=3, broker_id='IB',
                                      inst_id=3,
                                      action=OrdAction.BUY, type=OrdType.LIMIT,
                                      qty=10, limit_price=16.01,
                                      stop_price=17.5, tif=TIF.DAY, oca_tag="WTF", params=None)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_new_order_req, 'new_order_reqs')

    @parameterized.expand(params)
    def test_order_replace_request(self, name, datastore):
        persistable = OrderReplaceRequest(timestamp=clock.now(), cl_id=1, cl_ord_id=1, type=OrdType.LIMIT,
                                          qty=12, limit_price=13.2, stop_price=13.5, tif=TIF.DAY, oca_tag="WTF",
                                          params=None)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_ord_replace_req, 'ord_replace_reqs')

    @parameterized.expand(params)
    def test_order_cancel_request(self, name, datastore):
        persistable = OrderCancelRequest(timestamp=clock.now(), cl_id=1, cl_ord_id=1, params=None)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_ord_cancel_req, 'ord_cancel_reqs')

    # Execution Event

    @parameterized.expand(params)
    def test_order_status_update(self, name, datastore):
        persistable = OrderStatusUpdate(ord_status_id=10, broker_id="IB", ord_id=1, cl_id=1, cl_ord_id=1, inst_id=3,
                                        timestamp=clock.now(),
                                        filled_qty=10,
                                        avg_price=15.6, status=OrdStatus.NEW)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_ord_status_upd, 'ord_status_upds')

    @parameterized.expand(params)
    def test_execution_report(self, name, datastore):
        persistable = ExecutionReport(broker_id="IB", ord_id=1, cl_id=1, cl_ord_id=1, inst_id=3,
                                      timestamp=clock.now(),
                                      er_id=None,
                                      last_qty=10, last_price=10.8,
                                      filled_qty=140, avg_price=21.2, commission=18,
                                      status=OrdStatus.NEW)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_exec_report, 'exec_reports')

    # Account Event

    @parameterized.expand(params)
    def test_account_update(self, name, datastore):
        persistable = AccountUpdate("TEST", "TEST_account", "Pnl", "USD", 286.8, timestamp=clock.now())
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_account_update, 'account_updates')

    @parameterized.expand(params)
    def test_portfolio_update(self, name, datastore):
        persistable = PortfolioUpdate(upd_id=1, portf_id="test", inst_id=4, position=100, mkt_price=26.1,
                                      mkt_value=2610, avg_cost=24, unrealized_pnl=210.0, realized_pnl=0.0,
                                      account_name="TEST", timestamp=clock.now())
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_portfolio_update, 'portfolio_updates')

    # Ref Data

    @parameterized.expand(params)
    def test_instrument(self, name, datastore):
        persistable = Instrument(3, "Google", "STK", "GOOG", "SMART", "USD", alt_symbols={"IB": "GOOG"},
                                 alt_exch_id=None,
                                 sector=None, industry=None,
                                 put_call=None, expiry_date=None, und_inst_id=None, factor=1, strike=0.0, margin=0.0)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_instrument, 'instruments')

    @parameterized.expand(params)
    def test_exchange(self, name, datastore):
        persistable = Exchange("SEHK", "SEHK")
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_exchange, 'exchanges')

    @parameterized.expand(params)
    def test_currency(self, name, datastore):
        persistable = Currency("USD", "US Dollar")
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_currency, 'currencies')

    # Trade Data

    @parameterized.expand(params)
    def test_order(self, name, datastore):
        nos = NewOrderRequest(timestamp=None, cl_id=None, cl_ord_id=None, portf_id=None, broker_id=None, inst_id=None,
                              action=None, type=None,
                              qty=0, limit_price=0,
                              stop_price=0, tif=TIF.DAY, oca_tag=None, params=None)
        persistable = Order(nos=nos)
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_order, 'orders')

    @parameterized.expand(params)
    def test_account(self, name, datastore):
        persistable = Account(acct_id="test account")
        DataStoreTest.save_load(name, persistable, datastore, datastore.save_account, 'accounts')

    @parameterized.expand(params)
    def test_trading_config(self, name, datastore):
        instrument = 0

        dates = [datetime(2000, 1, 1), datetime(2015, 1, 1)]

        persistable = BacktestingConfig(stg_id="sma", portfolio_id='test',
                                        instrument_ids=[instrument],
                                        subscription_types=[
                                            BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                                        from_date=dates[0], to_date=dates[-1],
                                        broker_id=Broker.Simulator,
                                        feed_id=Feed.PandasMemory)

        DataStoreTest.save_load(name, persistable, datastore, datastore.save_config, 'configs')

    # @parameterized.expand(params)
    # def test_portfolio(self, name, datastore):
    #     persistable = Portfolio(portf_id="test1", cash=1000)
    #     DataStoreTest.save_load(name, persistable, datastore, datastore.save_portfolio, 'portfolios')

    @parameterized.expand(params)
    def test_strategy(self, name, datastore):
        instrument = 0

        dates = [datetime(2000, 1, 1), datetime(2015, 1, 1)]

        conf = BacktestingConfig(stg_id="sma", portfolio_id='test',
                                 instrument_ids=[instrument],
                                 subscription_types=[
                                     BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                                 from_date=dates[0], to_date=dates[-1],
                                 broker_id=Broker.Simulator,
                                 feed_id=Feed.PandasMemory)

        stg = Strategy(stg_id='st1')
        # nos = NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
        #                       limit_price=18.5)
        #
        # order = Order(nos=nos)
        # stg.ord_reqs[nos.cl_ord_id] = nos
        # stg.orders[order.cl_ord_id] = order
        # stg.add_position(nos.inst_id, nos.cl_id, nos.cl_ord_id, nos.qty)
        # stg.update_position_price(time=0, inst_id=nos.inst_id, price=100)

        DataStoreTest.save_load(name, stg, datastore, datastore.save_strategy, 'strategies')

    @staticmethod
    def save_load(name, persistable, datastore, save_func, load_clazz):
        save_func(persistable)
        result = [item for item in datastore.load_all(load_clazz) if item.id() == persistable.id()]
        assert len(result) == 1
        item = result[0]
        print
        "===== %s" % name
        print
        persistable
        print
        item
        assert MapSerializer.extract_slot(persistable) == MapSerializer.extract_slot(item)

    @classmethod
    def setUpClass(cls):
        mongo.start(app_context=context)
        cassandra.start(app_context=context)
        inmemory.start(app_context=context)

    @classmethod
    def tearDownClass(cls):
        mongo.stop()
        cassandra.stop()
        inmemory.stop()


if __name__ == "__main__":
    import unittest

    runner = unittest.TextTestRunner()
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(DataStoreTest))
    runner.run(test_suite)

    # creating a new test suite
    newSuite = unittest.TestSuite()
