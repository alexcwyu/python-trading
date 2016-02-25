from algotrader.event.execution import *
from algotrader.provider.broker import *
from algotrader.tools.singleton import *

from algotrader.tools import *
from algotrader.trading import clock


@singleton
class OrderManager(OrderEventHandler, ExecutionEventHandler, MarketDataEventHandler):
    # __metaclass__ = Singleton

    def __init__(self):
        self.__next_ord_id = 0

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)
        EventBus.execution_subject.subscribe(self.on_next)

    def next_ord_id(self):
        next_ord_id = self.__next_ord_id
        self.__next_ord_id += 1
        return next_ord_id

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

    def send_order(self, order):
        get_broker(order.broker_id).on_order(order)


order_mgr = OrderManager()
