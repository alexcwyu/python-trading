import logging
import time
from datetime import date, timedelta

from algotrader.event import EventBus
from algotrader.event.order import *
from algotrader.provider import *
from algotrader.provider.broker.ib.ib_broker import IBBroker
from algotrader.utils import logger


class EventLogger(ExecutionEventHandler, MarketDataEventHandler):
    def __init__(self):
        EventBus.data_subject.subscribe(self.on_next)
        EventBus.execution_subject.subscribe(self.on_next)

    def on_ord_upd(self, ord_upd):
        logger.info(ord_upd)

    def on_exec_report(self, exec_report):
        logger.info(exec_report)

    def on_bar(self, bar):
        logger.info(bar)

    def on_quote(self, quote):
        logger.info(quote)

    def on_trade(self, trade):
        logger.info(trade)

    def on_market_depth(self, market_depth):
        logger.info(market_depth)

today = date.today()
cl_ord_id = 1

def next_cl_ord_id():
    global cl_ord_id
    current_id = cl_ord_id
    cl_ord_id += 1
    return current_id

def sub_hist_data(broker, inst_id, day_ago):
    sub_key = HistDataSubscriptionKey(inst_id=inst_id, provider_id=IBBroker.ID, data_type=Bar, bar_size=BarSize.D1, from_date=(today - timedelta(days=day_ago)), to_date=today)
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


def test_mkt_order(broker , instrument=3, action=OrdAction.BUY, qty=1000):
    print "### testing market order"
    cl_ord_id = next_cl_ord_id()
    order = Order(cl_ord_id=cl_ord_id, instrument=instrument, action=action, type=OrdType.MARKET, qty=1000)
    broker.on_order(order)
    time.sleep(10)


def test_lmt_order_update_cancel(broker, instrument=3, qty=1000, limit_price=100):
    print "### testing limit order"
    cl_ord_id = next_cl_ord_id()
    order = Order(cl_ord_id=cl_ord_id, instrument=instrument, action=OrdAction.BUY, type=OrdType.LIMIT, qty=qty, limit_price=limit_price)
    broker.on_order(order)
    time.sleep(10)

    print "### testing order update"
    order = Order(cl_ord_id=cl_ord_id, instrument=instrument, action=OrdAction.BUY, type=OrdType.LIMIT, qty=qty * 2, limit_price=limit_price * 1.2)
    broker.on_ord_update_req(order)
    time.sleep(10)

    print "### testing order cancel"
    broker.on_ord_cancel_req(order)
    time.sleep(10)



if __name__ == "__main__":
    broker = IBBroker()
    broker.start()
    logger.setLevel(logging.DEBUG)
    eventLogger = EventLogger()

    # test_sub_hist_bar(broker)
    # test_sub_realtime_bar(broker)
    # test_sub_realtime_trade(broker)
    # test_sub_realtime_quote(broker)

    test_lmt_order_update_cancel(broker)
    test_mkt_order(broker, action=OrdAction.BUY)
    test_mkt_order(broker, action=OrdAction.SELL)
