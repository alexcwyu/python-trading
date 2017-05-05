from gevent import monkey

monkey.patch_all()
import logging
from datetime import date, timedelta

from algotrader.event.market_data import Bar
from algotrader.event.order import NewOrderRequest, OrdAction, OrdType, OrderReplaceRequest
from algotrader.provider.subscription import SubscriptionKey, HistDataSubscriptionKey, QuoteSubscriptionType, TradeSubscriptionType
from algotrader.config.app import RealtimeMarketDataImporterConfig
from algotrader.config.broker import IBConfig
from algotrader.config.persistence import MongoDBConfig
from algotrader.config.persistence import PersistenceConfig
from algotrader.event.market_data import BarSize, BarType
from algotrader.provider.broker import Broker
from algotrader.provider.datastore import PersistenceMode
from algotrader.provider.datastore import DataStore
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils import logger
from algotrader.trading.clock import Clock
import time


today = date.today()
cl_ord_id = 1


def next_cl_ord_id():
    global cl_ord_id
    current_id = cl_ord_id
    cl_ord_id += 1
    return current_id


def sub_hist_data(broker, inst_id, day_ago):
    sub_key = HistDataSubscriptionKey(inst_id=inst_id, provider_id=Broker.IB,
                                      subscription_type=BarSubscriptionType(data_type=Bar, bar_size=BarSize.D1),
                                      from_date=(today - timedelta(days=day_ago)), to_date=today)
    broker.subscribe_mktdata(sub_key)
    return sub_key


def sub_realtime_bar(broker, inst_id):
    sub_key = SubscriptionKey(inst_id=inst_id, provider_id=Broker.IB,
                              subscription_type=BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.S5))
    broker.subscribe_mktdata(sub_key)
    return sub_key


def sub_realtime_trade(broker, inst_id):
    sub_key = SubscriptionKey(inst_id=inst_id, provider_id=Broker.IB, subscription_type=TradeSubscriptionType())
    broker.subscribe_mktdata(sub_key)
    return sub_key


def sub_realtime_quote(broker, inst_id):
    sub_key = SubscriptionKey(inst_id=inst_id, provider_id=Broker.IB, subscription_type=QuoteSubscriptionType())
    broker.subscribe_mktdata(sub_key)
    return sub_key


def test_sub_hist_bar(broker):
    print "### requesting hist bar"
    sub_key = sub_hist_data(broker, 3, 5)
    time.sleep(5)
    print "### cancelling hist bar"
    broker.unsubscribe_mktdata(sub_key)
    time.sleep(2)


def test_sub_realtime_bar(broker):
    print "### requesting realtime bar"
    sub_key = sub_realtime_bar(broker, 3)
    time.sleep(20)
    print "### cancelling realtime bar"
    broker.unsubscribe_mktdata(sub_key)
    time.sleep(2)


def test_sub_realtime_trade(broker):
    print "### requesting realtime trade"
    sub_key = sub_realtime_trade(broker, 3)
    time.sleep(20)
    print "### cancelling realtime trade"
    broker.unsubscribe_mktdata(sub_key)
    time.sleep(2)


def test_sub_realtime_quote(broker):
    print "### requesting realtime quote"
    sub_key = sub_realtime_quote(broker, 3)
    time.sleep(20)
    print "### cancelling realtime quote"
    broker.unsubscribe_mktdata(sub_key)
    time.sleep(2)


def test_mkt_order(broker, inst_id=3, action=OrdAction.BUY, qty=1000):
    print "### testing market order"
    cl_ord_id = next_cl_ord_id()
    order = NewOrderRequest(cl_ord_id=cl_ord_id, inst_id=inst_id, action=action, type=OrdType.MARKET, qty=1000)
    broker.on_new_ord_req(order)
    time.sleep(10)


def test_lmt_order_update_cancel(broker, inst_id=3, qty=1000, limit_price=100):
    print "### testing limit order"
    cl_ord_id = next_cl_ord_id()
    order = NewOrderRequest(cl_id=1, cl_ord_id=1, inst_id=inst_id, action=OrdAction.BUY, type=OrdType.LIMIT, qty=qty,
                            limit_price=limit_price)
    broker.on_new_ord_req(order)
    time.sleep(5)

    print "### testing order update"
    order = OrderReplaceRequest(cl_id=1, cl_ord_id=1, type=OrdType.LIMIT, qty=qty * 2,
                                limit_price=limit_price * 1.2)
    broker.on_ord_replace_req(order)
    time.sleep(5)

    print "### testing order cancel"
    broker.on_ord_cancel_req(order)
    time.sleep(5)


if __name__ == "__main__":

    logger.setLevel(logging.DEBUG)

    persistence_config = PersistenceConfig(None,
                                           DataStore.InMemory, PersistenceMode.RealTime,
                                           DataStore.InMemory, PersistenceMode.RealTime,
                                           DataStore.InMemory, PersistenceMode.RealTime,
                                           DataStore.InMemory, PersistenceMode.RealTime)
    app_config = RealtimeMarketDataImporterConfig(None, RefDataManager.InMemory, Clock.RealTime,
                                              Broker.IB, [3],
                                              [BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                                              persistence_config,
                                              MongoDBConfig(), IBConfig(client_id=2, use_gevent=True))
    app_context = ApplicationContext(app_config=app_config)

    app_context.start()
    broker = app_context.provider_mgr.get(Broker.IB)
    broker.start(app_context)

    # test_sub_hist_bar(broker)
    test_sub_realtime_bar(broker)

    time.sleep(1000)

    # test_sub_realtime_trade(broker)
    # test_sub_realtime_quote(broker)