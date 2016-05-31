# from rx.concurrency import GEventScheduler
# from rx.observable import Observable, Observer
# import rx

from rx.subjects import Subject
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.event.order import ExecutionEventHandler
from algotrader.utils import logger


class EventBus(object):
    data_subject = Subject()
    order_subject = Subject()
    execution_subject = Subject()


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
