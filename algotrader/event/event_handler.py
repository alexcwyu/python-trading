from rx import Observer

from algotrader.event.event_bus import EventBus
from algotrader.utils import logger
import abc
from algotrader import Startable


class EventHandler(Observer, Startable):
    __metaclass__ = abc.ABCMeta

    def on_next(self, event):
        event.on(self)

    def on_error(self, err):
        logger.debug("[%s] Error: %s" % (self.__class__.__name__, err))

    def on_completed(self):
        logger.debug("[%s] Completed" % self.__class__.__name__)

    def _start(self, app_context=None):
        pass

    def _stop(self):
        pass


class MarketDataEventHandler(EventHandler):
    __metaclass__ = abc.ABCMeta

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))

    def on_market_depth(self, market_depth):
        logger.debug("[%s] %s" % (self.__class__.__name__, market_depth))


class OrderEventHandler(EventHandler):
    __metaclass__ = abc.ABCMeta

    # Sync interface, return Order
    def send_order(self, new_ord_req):
        raise NotImplementedError()

    # Sync interface, return Order
    def cancel_order(self, ord_cancel_req):
        raise NotImplementedError()

    # Sync interface, return Order
    def replace_order(self, ord_replace_req):
        raise NotImplementedError()

    # Async interface
    def on_new_ord_req(self, new_ord_req):
        logger.debug("[%s] %s" % (self.__class__.__name__, new_ord_req))
        self.send_order(new_ord_req)

    # Async interface
    def on_ord_replace_req(self, ord_replace_req):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_replace_req))
        self.replace_order(ord_replace_req)

    # Async interface
    def on_ord_cancel_req(self, ord_cancel_req):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_cancel_req))
        self.cancel_order(ord_cancel_req)


class ExecutionEventHandler(EventHandler):
    __metaclass__ = abc.ABCMeta

    def on_ord_upd(self, ord_upd):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_upd))

    def on_exec_report(self, exec_report):
        logger.debug("[%s] %s" % (self.__class__.__name__, exec_report))


class AccountEventHandler(EventHandler):
    __metaclass__ = abc.ABCMeta

    def on_acc_upd(self, acc_upd):
        logger.debug("[%s] %s" % (self.__class__.__name__, acc_upd))

    def on_portf_upd(self, portf_upd):
        logger.debug("[%s] %s" % (self.__class__.__name__, portf_upd))


class EventLogger(ExecutionEventHandler, MarketDataEventHandler):
    def __init__(self, data_subject=None, execution_subject=None):
        self.data_subject = data_subject if data_subject else EventBus.data_subject
        self.execution_subject = execution_subject if execution_subject else EventBus.execution_subject

        self.data_subject.subscribe(self.on_next)
        self.execution_subject.subscribe(self.on_next)

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
