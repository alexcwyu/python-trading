from algotrader.event import *
import abc
from atom.api import Atom, Unicode, Range, Bool, observe, Enum, Str, Value, Float, Long, List

class OrderEvent(Event):
    pass


class OrdAction:
    BUY = 1
    SELL = 2


class OrdType:
    MARKET = 1
    LIMIT = 2
    STOP = 3
    STOP_LIMIT = 4
    TRAILING_STOP = 5


class TIF:
    DAY = 1
    GTC = 2
    FOK = 3


class OrdStatus:
    NEW = 1
    PENDING_SUBMIT = 2
    SUBMITTED = 3
    PENDING_CANCEL = 4
    CANCELLED = 5
    PENDING_REPLACE = 6
    REPLACED = 7
    PARTIALLY_FILLED = 8
    FILLED = 9
    REJECTED = 10


class ExecutionEvent(Event):
    broker_id = Str()
    ord_id = Long()
    instrument = Str()
    timestamp = Value(current_time)


class OrderStatusUpdate(ExecutionEvent):
    status = Enum(OrdStatus.NEW,
                  OrdStatus.PENDING_SUBMIT, OrdStatus.SUBMITTED,
                  OrdStatus.PENDING_CANCEL, OrdStatus.CANCELLED,
                  OrdStatus.PENDING_REPLACE, OrdStatus.REPLACED,
                  OrdStatus.PARTIALLY_FILLED, OrdStatus.FILLED,
                  OrdStatus.REJECTED)

    def on(self, handler):
        handler.on_ord_upd(self)

    def __repr__(self):
        return "OrderStatusUpdate(broker_id = %s, ord_id = %s,instrument = %s, timestamp = %s, status = %s)" \
               % (self.broker_id, self.ord_id, self.instrument, self.timestamp, self.status)


class ExecutionReport(OrderStatusUpdate):
    er_id = Long()
    filled_qty = Float()
    filled_price = Float()
    commission = Float()

    def on(self, handler):
        handler.on_exec_report(self)

    def __repr__(self):
        return "ExecutionReport(broker_id = %s, ord_id = %s,instrument = %s, timestamp = %s" \
               ", er_id = %s, filled_qty = %s, filled_price = %s, commission = %s)" \
               % (self.broker_id, self.ord_id, self.instrument, self.timestamp,
                  self.er_id, self.filled_qty, self.filled_price, self.commission)


class Order(OrderEvent):
    instrument = Str()
    timestamp = Value(current_time)

    ord_id = Long()
    stg_id = Str()
    broker_id = Str()
    action = Enum(OrdAction.BUY, OrdAction.SELL)
    type = Enum(OrdType.MARKET, OrdType.LIMIT, OrdType.STOP, OrdType.STOP_LIMIT, OrdType.TRAILING_STOP)
    tif = Enum(TIF.DAY, TIF.GTC, TIF.FOK)
    status = Enum(OrdStatus.NEW,
                  OrdStatus.PENDING_SUBMIT, OrdStatus.SUBMITTED,
                  OrdStatus.PENDING_CANCEL, OrdStatus.CANCELLED,
                  OrdStatus.PENDING_REPLACE, OrdStatus.REPLACED,
                  OrdStatus.PARTIALLY_FILLED, OrdStatus.FILLED,
                  OrdStatus.REJECTED)

    qty = Float(0)
    limit_price = Float(0)
    stop_price = Float(0)

    filled_qty = Float(0)
    avg_price = Float(0)

    last_qty = Float(0)
    last_price = Float(0)

    stop_price = Float(0)

    stop_limit_ready = Bool(False)

    trailing_stop_exec_price = Float(0)

    exec_reports = List(item=ExecutionReport, default=[])
    update_events = List(item=OrderStatusUpdate, default=[])

    def on(self, handler):
        handler.on_order(self)

    def __repr__(self):
        return "Order(instrument = %s, timestamp = %s,ord_id = %s, stg_id = %s, broker_id = %s, action = %s, type = %s, tif = %s, status = %s" \
               ", qty = %s, limit_price = %s, stop_price = %s, filled_qty = %s, avg_price = %s, last_qty = %s, last_price = %s ,stop_price = %s" \
               ", stop_limit_ready = %s , trailing_stop_exec_price = %s , exec_reports = %s , update_events = %s)" \
               % (self.instrument, self.timestamp, self.ord_id, self.stg_id, self.broker_id, self.action, self.type,
                  self.tif,
                  self.status,
                  self.qty, self.limit_price, self.stop_price, self.filled_qty, self.avg_price, self.last_qty,
                  self.last_price, self.stop_price, self.stop_limit_ready, self.trailing_stop_exec_price, self.exec_reports, self.update_events)

    def add_exec_report(self, exec_report):
        if exec_report.ord_id != self.ord_id:
            raise Exception("exec_report [%s] order_id [%s] is not same as current order id [%s]" %(exec_report.er_id, exec_report.ord_id, self.ord_id))

        self.exec_reports.append(exec_report)
        self.last_price = exec_report.filled_price
        self.last_qty = exec_report.filled_qty
        self.avg_price = ((self.avg_price * self.filled_qty) + (exec_report.filled_price * exec_report.filled_qty)) / (
            self.filled_qty + exec_report.filled_qty)
        self.filled_qty += exec_report.filled_qty

        if self.qty == self.filled_qty:
            self.status = OrdStatus.FILLED
        elif self.qty > self.filled_qty:
            self.status = OrdStatus.PARTIALLY_FILLED
        else:
            raise Exception("filled qty %s is greater than ord qty %s" %(self.filled_qty, self.qty))

    def update_status(self, ord_upd):
        if ord_upd.ord_id != self.ord_id:
            raise Exception("ord_upd  order_id [%s] is not same as current order id [%s]" %(ord_upd.ord_id, self.ord_id))

        self.update_events.append(ord_upd)
        self.status = ord_upd.status

    def is_done(self):
        return self.status == OrdStatus.REJECTED or self.status == OrdStatus.CANCELLED or self.status == OrdStatus.FILLED

    def is_active(self):
        return self.status == OrdStatus.NEW or self.status == OrdStatus.PENDING_SUBMIT or self.status == OrdStatus.SUBMITTED \
               or self.status == OrdStatus.PARTIALLY_FILLED or self.status == OrdStatus.REPLACED

    def leave_qty(self):
        return self.qty - self.filled_qty


class ExecutionEventHandler(EventHandler):
    def on_ord_upd(self, ord_upd):
        pass

    def on_exec_report(self, exec_report):
        pass


class OrderEventHandler(EventHandler):
    def on_order(self, order):
        pass


if __name__ == "__main__":
    order = Order()
    print order.avg_price
    print order.status
