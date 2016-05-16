from algotrader.event import *


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
    __slots__ = (
        'broker_id',
        'ord_id',
        'instrument',
        'timestamp'
    )

    def __init__(self, broker_id=None, ord_id=None, instrument=None, timestamp=None):
        # super(ExecutionEvent, self).__init__(instrument, timestamp)
        self.broker_id = broker_id
        self.ord_id = ord_id
        self.instrument = instrument
        self.timestamp = timestamp


class OrderStatusUpdate(ExecutionEvent):
    __slots__ = (
        'status'
    )

    def __init__(self, broker_id=None, ord_id=None, instrument=None, timestamp=None, status=OrdStatus.NEW):
        super(OrderStatusUpdate, self).__init__(broker_id, ord_id, instrument, timestamp)
        self.status = status
        self.ord_id = ord_id
        self.instrument = instrument
        self.timestamp = timestamp

    def on(self, handler):
        handler.on_ord_upd(self)

    def __repr__(self):
        return "OrderStatusUpdate(broker_id = %s, ord_id = %s,instrument = %s, timestamp = %s, status = %s)" \
               % (self.broker_id, self.ord_id, self.instrument, self.timestamp, self.status)


class ExecutionReport(OrderStatusUpdate):
    __slots__ = (
        'er_id',
        'filled_qty',
        'filled_price',
        'commission'
    )

    def __init__(self, broker_id=None, ord_id=None, instrument=None, timestamp=None, er_id=None, filled_qty=0, filled_price=0, commission=0,
                 status=OrdStatus.NEW):
        super(ExecutionReport, self).__init__(broker_id, ord_id, instrument, timestamp, status)
        self.er_id = er_id
        self.filled_qty = filled_qty
        self.filled_price = filled_price
        self.commission = commission

    def on(self, handler):
        handler.on_exec_report(self)

    def __repr__(self):
        return "ExecutionReport(broker_id = %s, ord_id = %s,instrument = %s, timestamp = %s" \
               ", er_id = %s, filled_qty = %s, filled_price = %s, commission = %s)" \
               % (self.broker_id, self.ord_id, self.instrument, self.timestamp,
                  self.er_id, self.filled_qty, self.filled_price, self.commission)


class Order(OrderEvent):
    __slots__ = (
        'instrument',
        'timestamp',
        'ord_id',
        'cl_ord_id',
        'stg_id',
        'broker_id',
        'oca_tag'
        'action',
        'type',
        'qty',
        'limit_price'
        'tif',
        'status',
        'filled_qty',
        'avg_price',
        'last_qty',
        'last_price',
        'stop_price',
        'stop_limit_ready',
        'trailing_stop_exec_price',
        'exec_reports',
        'update_events'
    )

    def __init__(self, instrument=None, ord_id=None, stg_id=None, broker_id=None, action=None, type=None, timestamp=None, qty=0, limit_price=0,
                 stop_price=0, status=OrdStatus.NEW, tif=TIF.DAY, cl_ord_id=None, oca_tag=None):
        self.instrument = instrument
        self.timestamp = timestamp
        self.ord_id = ord_id
        self.stg_id = stg_id
        self.cl_ord_id = cl_ord_id
        self.broker_id = broker_id
        self.oca_tag = oca_tag
        self.action = action
        self.type = type
        self.qty = qty
        self.limit_price = limit_price
        self.tif = tif
        self.status = status
        self.filled_qty = 0
        self.avg_price = 0
        self.last_qty = 0
        self.last_price = 0
        self.stop_price = stop_price
        self.stop_limit_ready = False
        self.trailing_stop_exec_price = 0
        self.exec_reports = []
        self.update_events = []

    def on(self, handler):
        handler.on_order(self)

    def __repr__(self):
        return "Order(instrument = %s, timestamp = %s,ord_id = %s, stg_id = %s, cl_ord_id = %s, broker_id = %s, action = %s, type = %s, tif = %s, status = %s" \
               ", qty = %s, limit_price = %s, stop_price = %s, filled_qty = %s, avg_price = %s, last_qty = %s, last_price = %s ,stop_price = %s" \
               ", stop_limit_ready = %s , trailing_stop_exec_price = %s , exec_reports = %s , update_events = %s)" \
               % (self.instrument, self.timestamp, self.ord_id, self.stg_id, self.cl_ord_id, self.broker_id, self.action, self.type,
                  self.tif,
                  self.status,
                  self.qty, self.limit_price, self.stop_price, self.filled_qty, self.avg_price, self.last_qty,
                  self.last_price, self.stop_price, self.stop_limit_ready, self.trailing_stop_exec_price,
                  self.exec_reports, self.update_events)

    def add_exec_report(self, exec_report):
        if exec_report.ord_id != self.ord_id:
            raise Exception("exec_report [%s] order_id [%s] is not same as current order id [%s]" % (
                exec_report.er_id, exec_report.ord_id, self.ord_id))

        self.exec_reports.append(exec_report)
        self.last_price = exec_report.filled_price
        self.last_qty = exec_report.filled_qty
        if self.filled_qty + exec_report.filled_qty != 0:
            self.avg_price = ((self.avg_price * self.filled_qty) + (
                exec_report.filled_price * exec_report.filled_qty)) / (
                                 self.filled_qty + exec_report.filled_qty)
        self.filled_qty += exec_report.filled_qty

        if self.qty == self.filled_qty:
            self.status = OrdStatus.FILLED
        elif self.qty > self.filled_qty:
            self.status = OrdStatus.PARTIALLY_FILLED
        else:
            raise Exception("filled qty %s is greater than ord qty %s" % (self.filled_qty, self.qty))

    def update_status(self, ord_upd):
        if ord_upd.ord_id != self.ord_id:
            raise Exception(
                "ord_upd  order_id [%s] is not same as current order id [%s]" % (ord_upd.ord_id, self.ord_id))

        self.update_events.append(ord_upd)
        self.status = ord_upd.status

    def is_done(self):
        return self.status == OrdStatus.REJECTED or self.status == OrdStatus.CANCELLED or self.status == OrdStatus.FILLED

    def is_active(self):
        return self.status == OrdStatus.NEW or self.status == OrdStatus.PENDING_SUBMIT or self.status == OrdStatus.SUBMITTED \
               or self.status == OrdStatus.PARTIALLY_FILLED or self.status == OrdStatus.REPLACED

    def leave_qty(self):
        return self.qty - self.filled_qty

    def is_buy(self):
        return self.action == OrdAction.BUY

    def is_sell(self):
        return self.action == OrdAction.SELL

class ExecutionEventHandler(EventHandler):
    def on_ord_upd(self, ord_upd):
        pass

    def on_exec_report(self, exec_report):
        pass


class OrderEventHandler(EventHandler):
    def on_order(self, order):
        pass
