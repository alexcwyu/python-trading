from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.event.order import OrderEventHandler, ExecutionEventHandler
from algotrader.provider import broker_mgr
from algotrader.strategy.strategy_mgr import stg_mgr
from algotrader.utils import logger


class OrderManager(OrderEventHandler, ExecutionEventHandler, MarketDataEventHandler):
    def __init__(self):
        self.__next_ord_id = 0
        self.__orders = {}

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
        self.send_order(order)

    def on_ord_upd(self, ord_upd):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_upd))
        order = self.__orders[ord_upd.ord_id]
        stg = stg_mgr.get_strategy(order.stg_id)
        stg.on_ord_upd(ord_upd)

    def on_exec_report(self, exec_report):
        logger.debug("[%s] %s" % (self.__class__.__name__, exec_report))
        order = self.__orders[exec_report.ord_id]
        stg = stg_mgr.get_strategy(order.stg_id)
        stg.on_exec_report(exec_report)

    def send_order(self, order):
        #order.ord_id = self.next_ord_id()
        self.__orders[order.ord_id] = order
        broker_mgr.get_broker(order.broker_id).on_order(order)
        return order


order_mgr = OrderManager()
