from rx.concurrency import GEventScheduler
from rx.observable import Observable, Observer
from rx.subjects import Subject
import rx

import logging
from algotrader.event.market_data import *
from algotrader.event.order import *
from algotrader.trading.order_mgr import *


class Strategy(OrderEventHandler, MarketDataEventHandler):
    def __init__(self, feed, broker_id):
        self.__feed = feed
        self.__broker_id = broker_id

    def run(self):
        getBroker(broker_id=self.__broker_id).start()
        EventBus.data_subject.subscribe(self.on_next)
        self.__feed.start()

    def on_bar(self, bar):
        print "[%s] %s" % (self.__class__.__name__, bar)

    def on_quote(self, quote):
        print "[%s] %s" % (self.__class__.__name__, quote)

    def on_trade(self, trade):
        print "[%s] %s" % (self.__class__.__name__, trade)

    def on_order(self, order):
        print "[%s] %s" % (self.__class__.__name__, order)

    def on_ord_upd(self, ord_upd):
        print "[%s] %s" % (self.__class__.__name__, ord_upd)

    def on_exec_report(self, exec_report):
        print "[%s] %s" % (self.__class__.__name__, exec_report)
