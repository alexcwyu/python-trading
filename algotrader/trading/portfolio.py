import logging
from algotrader.event.market_data import *
from algotrader.event.order import *
from algotrader.trading.order_mgr import *
from algotrader.tools import *


class Portfolio(OrderEventHandler, ExecutionEventHandler, MarketDataEventHandler):
    def __init__(self, amount):
        self.__amount = amount

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))

    def on_order(self, order):
        logger.debug("[%s] %s" % (self.__class__.__name__, order))

    def on_ord_upd(self, ord_upd):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_upd))

    def on_exec_report(self, exec_report):
        logger.debug("[%s] %s" % (self.__class__.__name__, exec_report))
