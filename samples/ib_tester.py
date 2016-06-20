import logging
import time
from datetime import date, timedelta

from algotrader.event import EventLogger
from algotrader.event.market_data import Bar, Trade, Quote, BarSize
from algotrader.event.order import Order, OrdAction, OrdType
from algotrader.provider.broker.ib.ib_broker import IBBroker
from algotrader.provider.provider import SubscriptionKey, HistDataSubscriptionKey
from algotrader.utils import logger

today = date.today()
cl_ord_id = 1


def next_cl_ord_id():
    global cl_ord_id
    current_id = cl_ord_id
    cl_ord_id += 1
    return current_id


def sub_hist_data(broker, inst_id, day_ago):
    sub_key = HistDataSubscriptionKey(inst_id=inst_id, provider_id=IBBroker.ID, data_type=Bar, bar_size=BarSize.D1,
                                      from_date=(today - timedelta(days=day_ago)), to_date=today)
    broker.subscribe_mktdata(sub_key)
    return sub_key


def sub_realtime_bar(broker, inst_id):
    sub_key = SubscriptionKey(inst_id=inst_id, provider_id=IBBroker.ID, data_type=Bar, bar_size=BarSize.S5)
    broker.subscribe_mktdata(sub_key)
    return sub_key


def sub_realtime_trade(broker, inst_id):
    sub_key = SubscriptionKey(inst_id=inst_id, provider_id=IBBroker.ID, data_type=Trade, bar_size=BarSize.S1)
    broker.subscribe_mktdata(sub_key)
    return sub_key


def sub_realtime_quote(broker, inst_id):
    sub_key = SubscriptionKey(inst_id=inst_id, provider_id=IBBroker.ID, data_type=Quote, bar_size=BarSize.S1)
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
    order = Order(cl_ord_id=cl_ord_id, inst_id=inst_id, action=action, type=OrdType.MARKET, qty=1000)
    broker.on_order(order)
    time.sleep(10)


def test_lmt_order_update_cancel(broker, inst_id=3, qty=1000, limit_price=100):
    print "### testing limit order"
    cl_ord_id = next_cl_ord_id()
    order = Order(cl_ord_id=cl_ord_id, inst_id=inst_id, action=OrdAction.BUY, type=OrdType.LIMIT, qty=qty,
                  limit_price=limit_price)
    broker.on_order(order)
    time.sleep(10)

    print "### testing order update"
    order = Order(cl_ord_id=cl_ord_id, inst_id=inst_id, action=OrdAction.BUY, type=OrdType.LIMIT, qty=qty * 2,
                  limit_price=limit_price * 1.2)
    broker.on_ord_update_req(order)
    time.sleep(10)

    print "### testing order cancel"
    broker.on_ord_cancel_req(order)
    time.sleep(10)


if __name__ == "__main__":
    broker = IBBroker(daemon=True)

    broker.start()
    logger.setLevel(logging.DEBUG)
    eventLogger = EventLogger()

    # test_sub_hist_bar(broker)
    # test_sub_realtime_bar(broker)
    test_sub_realtime_trade(broker)
    test_sub_realtime_quote(broker)

    # test_lmt_order_update_cancel(broker)
    # test_mkt_order(broker, action=OrdAction.BUY)
    # test_mkt_order(broker, action=OrdAction.SELL)
