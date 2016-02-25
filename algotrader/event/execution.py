from algotrader.event import *
import abc
from atom.api import Atom, Unicode, Range, Bool, observe, Enum, Str, Value, Float, Long
from .order import OrdType, OrdStatus


class ExecutionEvent(Event):
    broker_id = Str()
    ord_id = Long()
    instrument = Str()
    timestamp = Value(current_time)


class OrderStatusUpdate(ExecutionEvent):
    ord_status = Enum(OrdStatus.INITIAL, OrdStatus.PENDING_SUBMIT, OrdStatus.SUBMITTED, OrdStatus.PENDING_CANCEL,
                      OrdStatus.CANCELLED, OrdStatus.PARTIALLY_FILLED, OrdStatus.FILLED)

    def on(self, handler):
        handler.on_ord_upd(self)


class ExecutionReport(ExecutionEvent):
    er_id = Long()
    filled_qty = Float()
    filled_price = Float()
    commission = Float()

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
