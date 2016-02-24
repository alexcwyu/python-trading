from algotrader.event import *
import abc
from atom.api import Atom, Unicode, Range, Bool, observe, Enum, Str, Value, Float, Long


class ExecutionEvent(Event):
    symbol = Str()
    timestamp = Value(current_time)

    def __init__(self, symbol, timestamp):
        self.symbol = symbol
        self.timestamp = timestamp


class OrderStatusUpdate(ExecutionEvent):
    def on(self, handler):
        handler.on_ord_upd(self)


class ExecutionReport(ExecutionEvent):
    def on(self, handler):
        handler.on_exec_report(self)


class ExecutionEventHandler(EventHandler):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def on_ord_upd(self, ord_upd):
        pass

    @abc.abstractmethod
    def on_exec_report(self, exec_report):
        pass
