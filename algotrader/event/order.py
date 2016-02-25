from algotrader.event import *
import abc
from atom.api import Atom, Unicode, Range, Bool, observe, Enum, Str, Value, Float, Long
from algotrader.tools import *


class OrderEvent(Event):
    pass

#
# class OrdAction:
#     BUY = 1
#     SELL = 2


class OrdType:
    MARKET = 1
    LIMIT = 2
    STOP = 3
    STOP_LIMIT = 4


class TIF:
    DAY = 1
    GTC = 2
    FOK = 3


class OrdStatus:
    INITIAL = 1
    PENDING_SUBMIT = 2
    SUBMITTED = 3
    PENDING_CANCEL = 4
    CANCELLED = 5
    PARTIALLY_FILLED = 6
    FILLED = 7


class Order(OrderEvent):
    instrument = Str()
    timestamp = Value(current_time)

    ord_id = Long()
    stg_id = Str()
    broker_id = Str()
    #action = Enum(OrdAction.BUY, OrdAction.SELL)
    type = Enum(OrdType.MARKET, OrdType.LIMIT, OrdType.STOP, OrdType.STOP_LIMIT)
    tif = Enum(TIF.DAY, TIF.GTC, TIF.FOK)
    status = Enum(OrdStatus.INITIAL, OrdStatus.PENDING_SUBMIT, OrdStatus.SUBMITTED, OrdStatus.PENDING_CANCEL,
                  OrdStatus.CANCELLED, OrdStatus.PARTIALLY_FILLED, OrdStatus.FILLED)

    qty = Float()
    limit_price = Float()
    stop_price = Float()

    filled_qty = Float()
    avg_price = Float()

    last_qty = Float()
    last_price = Float()

    def on(self, handler):
        handler.on_order(self)


class OrderEventHandler(EventHandler):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def on_order(self, order):
        pass


if __name__ == "__main__":
    order = Order()
    print order.avg_price
    print order.status
