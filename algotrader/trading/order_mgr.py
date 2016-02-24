from algotrader.event.execution import *
from algotrader.provider.broker import *
from algotrader.tools.singleton import *


@singleton
class OrderManager(OrderEventHandler, ExecutionEventHandler, MarketDataEventHandler):
    # __metaclass__ = Singleton

    def __init__(self):
        EventBus.data_subject.subscribe(self.on_next)
        self.__next_ord_id = 0

    def next_ord_id(self):
        next_ord_id = self.__next_ord_id
        self.__next_ord_id+=1
        return next_ord_id

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

    def new_market_order(self, instrument, qty, brokerId):
        getBroker(brokerId).on_order()
        pass

    def new_limit_order(self, instrument, qty, price):
        pass


order_mgr = OrderManager()
