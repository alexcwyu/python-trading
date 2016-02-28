from rx.concurrency import GEventScheduler
from rx.observable import Observable, Observer
from rx.subjects import Subject
import rx

import logging
from algotrader.event.market_data import *
from algotrader.event.order import *
from algotrader.trading.order_mgr import *
from algotrader.tools import *
from algotrader.trading.portfolio import *


class Strategy(OrderEventHandler, MarketDataEventHandler):
    def __init__(self, stg_id, broker_id, feed, portfolio):
        self.__stg_id = stg_id
        self.__broker_id = broker_id
        self.__feed = feed
        self.__portfolio = portfolio

    def start(self):
        broker = get_broker(broker_id=self.__broker_id)
        broker.start()
        self.__portfolio.start()
        EventBus.data_subject.subscribe(self.on_next)
        self.__feed.start()

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__portfolio.on_bar(bar)

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__portfolio.on_quote(quote)

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__portfolio.on_trade(trade)

    def on_order(self, order):
        logger.debug("[%s] %s" % (self.__class__.__name__, order))
        self.__portfolio.on_order(order)

    def on_ord_upd(self, ord_upd):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_upd))
        self.__portfolio.on_ord_upd(ord_upd)

    def on_exec_report(self, exec_report):
        logger.debug("[%s] %s" % (self.__class__.__name__, exec_report))
        self.__portfolio.on_exec_report(exec_report)

    def new_market_order(self, instrument, qty, tif=TIF.DAY):
        self.new_order(instrument, OrdType.MARKET, qty, 0.0, tif)

    def new_limit_order(self, instrument, qty, price, tif=TIF.DAY):
        self.new_order(instrument, OrdType.LIMIT, qty, price, tif)

    def new_order(self, instrument, ord_type, qty, price, tif=TIF.DAY):
        order = Order(instrument=instrument, timestamp=clock.default_clock.current_date_time(),
                      ord_id=order_mgr.next_ord_id(), stg_id=self.__stg_id, broker_id=self.__broker_id, type=ord_type,
                      tif=tif, qty=qty,
                      limit_price=price)
        order_mgr.send_order(order)
