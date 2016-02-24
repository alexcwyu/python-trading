from algotrader.event import *
import abc
from atom.api import Atom, Unicode, Range, Bool, observe, Enum, Str, Value, Float, Long


class OrderEvent(Event):
    symbol = Str()
    timestamp = Value(current_time)
    ord_id = Long()
    pass


class Order(OrderEvent):
    class Action:
        BUY = 1
        SELL = 2

    class Type:
        MARKET = 1
        LIMIT = 2
        STOP = 3
        STOP_LIMIT = 4

    class TIF:
        DAY = 1
        GTC = 2
        FOK = 3

    class Status:
        INITIAL = 1
        PENDING_SUBMIT = 2
        SUBMITTED = 3
        PENDING_CANCEL = 4
        CANCELLED = 5
        PARTIALLY_FILLED = 6
        FILLED = 7

    stg_id = Str()
    broker_id = Str()
    action = Enum(Action.BUY, Action.SELL)
    type = Enum(Type.MARKET, Type.LIMIT, Type.STOP, Type.STOP_LIMIT)
    tif = Enum(TIF.DAY, TIF.GTC, TIF.FOK)
    status = Enum(Status.INITIAL, Status.PENDING_SUBMIT, Status.SUBMITTED, Status.PENDING_CANCEL, Status.CANCELLED,
                  Status.PARTIALLY_FILLED, Status.FILLED)

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
    print "started"
    order = Order()
    order.stg_id = "test"
    order.action = Order.Action.BUY
    print order.stg_id
    print order.action
