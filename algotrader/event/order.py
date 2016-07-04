from algotrader.event.event import Event, EventHandler


class OrderEvent(Event):
    def __init__(self, timestamp=None):
        super(OrderEvent, self).__init__(timestamp)


class OrdAction:
    BUY = 1
    SELL = 2
    SSHORT = 3


class OrdType:
    MARKET = 1
    LIMIT = 2
    STOP = 3
    STOP_LIMIT = 4
    TRAILING_STOP = 5
    MARKET_ON_CLOSE = 6
    LIMIT_ON_CLOSE = 7
    MARKET_TO_LIMIT = 8
    MARKET_IF_PRICE_TOUCHED = 9
    MARKET_ON_OPEN = 10


class TIF:
    DAY = 1
    GTC = 2
    FOK = 3
    GTD = 4


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
    UNKNOWN = -1


class ExecutionEvent(Event):
    __slots__ = (
        'broker_id',
        'ord_id',
        'cl_ord_id',
        'inst_id',
    )

    def __init__(self, broker_id=None, ord_id=None, cl_ord_id=None, inst_id=None, timestamp=None):
        super(ExecutionEvent, self).__init__(timestamp)
        self.broker_id = broker_id
        self.ord_id = ord_id
        self.cl_ord_id = cl_ord_id
        self.inst_id = inst_id


class OrderStatusUpdate(ExecutionEvent):
    __slots__ = (
        'filled_qty',
        'avg_price',
        'status',

    )

    def __init__(self, broker_id=None, ord_id=None, cl_ord_id=None, inst_id=None, timestamp=None, filled_qty=0,
                 avg_price=0, status=OrdStatus.NEW):
        super(OrderStatusUpdate, self).__init__(broker_id=broker_id, ord_id=ord_id, cl_ord_id=cl_ord_id,
                                                inst_id=inst_id, timestamp=timestamp)
        self.filled_qty = filled_qty
        self.avg_price = avg_price
        self.status = status

    def on(self, handler):
        handler.on_ord_upd(self)

    def __repr__(self):
        return "OrderStatusUpdate(broker_id = %s, ord_id = %s, cl_ord_id=%s, inst_id = %s, timestamp = %s, status = %s)" \
               % (self.broker_id, self.ord_id, self.cl_ord_id, self.inst_id, self.timestamp, self.status)


class ExecutionReport(OrderStatusUpdate):
    __slots__ = (
        'er_id',
        'last_qty',
        'last_price'
        'commission'
    )

    def __init__(self, broker_id=None, ord_id=None, cl_ord_id=None, inst_id=None, timestamp=None, er_id=None,
                 last_qty=0, last_price=0,
                 filled_qty=0, avg_price=0, commission=0,
                 status=OrdStatus.NEW):
        super(ExecutionReport, self).__init__(broker_id=broker_id, ord_id=ord_id, cl_ord_id=cl_ord_id, inst_id=inst_id,
                                              timestamp=timestamp, filled_qty=filled_qty, avg_price=avg_price,
                                              status=status)
        self.er_id = er_id
        self.last_qty = last_qty
        self.last_price = last_price
        self.commission = commission

    def on(self, handler):
        handler.on_exec_report(self)

    def __repr__(self):
        return "ExecutionReport(broker_id = %s, ord_id = %s, cl_ord_id = %s, inst_id = %s, timestamp = %s" \
               ", er_id = %s, last_qty = %s, last_price = %s, filled_qty = %s, avg_price = %s, commission = %s)" \
               % (self.broker_id, self.ord_id, self.cl_ord_id, self.inst_id, self.timestamp,
                  self.er_id, self.last_qty, self.last_price, self.filled_qty, self.avg_price, self.commission)


class NewOrderRequest(OrderEvent):
    __slots__ = (
        'cl_ord_id',
        'cl_id',
        'broker_id',
        'inst_id',
        'action',
        'type',
        'qty',
        'limit_price'
        'stop_price',
        'tif',
        'oca_tag',
        'params'
    )

    def __init__(self, timestamp=None, cl_id=None, cl_ord_id=None, broker_id=None, inst_id=None, action=None, type=None,
                 qty=0, limit_price=0,
                 stop_price=0, tif=TIF.DAY, oca_tag=None, params=None):
        super(NewOrderSingle, self).__init__(timestamp=timestamp)
        self.inst_id = inst_id
        self.cl_id = cl_id
        self.cl_ord_id = cl_ord_id
        self.broker_id = broker_id
        self.action = action
        self.type = type
        self.qty = qty
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.tif = tif
        self.oca_tag = oca_tag
        self.params = params if params else {}

    def on(self, handler):
        handler.on_order(self)

    def __repr__(self):
        return "NewOrderRequest(timestamp = %s, inst_id = %s, cl_id = %s, cl_ord_id = %s, broker_id = %s, action = %s" \
               ", type = %s, qty = %s, limit_price = %s, stop_price = %s, tif = %s, oca_tag = %s, params = %s)" \
               % (self.timestamp, self.inst_id, self.cl_id, self.cl_ord_id, self.broker_id, self.action,
                  self.type, self.qty, self.limit_price, self.stop_price, self.tif, self.oca_tag, self.params)

    def is_buy(self):
        return self.action == OrdAction.BUY

    def is_sell(self):
        return self.action == OrdAction.SELL


class OrderReplaceRequest(OrderEvent):


class OrderCancelRequest(OrderEvent):


class Order()
    __slots__ = (
        'inst_id',
        'timestamp',
        'ord_id',
        'cl_id',
        'cl_ord_id',
        'broker_id',
        'action',
        'type',
        'qty',
        'limit_price'
        'stop_price',
        'tif',
        'oca_tag',
        'params',
        'status',
        'filled_qty',
        'avg_price',
        'last_qty',
        'last_price',
        'stop_limit_ready',
        'trailing_stop_exec_price',
        'ord_events',
        'exec_events',
    )

    def __init__(self, ord_id, nos = None):
        self.ord_id = ord_id
        if nos:
            self.on_new_order_request(nos)

    def on(self, handler):
        handler.on_order(self)

    def __repr__(self):
        return "Order(inst_id = %s, timestamp = %s,ord_id = %s, cl_id = %s, cl_ord_id = %s, broker_id = %s, action = %s, type = %s" \
               ", qty = %s, limit_price = %s, stop_price = %s, tif = %s, oca_tag = %s, params = %s" \
               ", status = %s, filled_qty = %s, avg_price = %s, last_qty = %s, last_price = %s ,stop_price = %s" \
               ", stop_limit_ready = %s , trailing_stop_exec_price = %s , ord_events = %s , exec_events = %s)" \
               % (self.inst_id, self.timestamp, self.ord_id, self.cl_id, self.cl_ord_id, self.broker_id, self.action, self.type,
                  self.qty, self.limit_price, self.stop_price, self.tif, self.oca_tag, self.params,
                  self.status, self.filled_qty, self.avg_price, self.last_qty, self.last_price, self.stop_price,
                  self.stop_limit_ready, self.trailing_stop_exec_price, self.ord_events, self.exec_events)

    def on_new_order_request(self, nos):
        self.inst_id = nos.inst_id
        self.timestamp = nos.timestamp
        self.cl_id = nos.cl_id
        self.cl_ord_id = nos.cl_ord_id
        self.broker_id = nos.broker_id
        self.action = nos.action
        self.type = nos.type
        self.qty = nos.qty
        self.limit_price = nos.limit_price
        self.tif = nos.tif
        self.oca_tag = nos.oca_tag
        self.params = nos.params
        self.status = OrdStatus.NEW
        self.filled_qty = 0
        self.avg_price = 0
        self.last_qty = 0
        self.last_price = 0
        self.stop_price = stop_price
        self.stop_limit_ready = False
        self.trailing_stop_exec_price = 0
        self.ord_events = [nos]
        self.exec_events = []


    def on_order_replace_request(self, ord_replace_req):
        self.ord_events.append(ord_replace_req)

    def on_order_cancel_request(self, ord_cancel_req):
        self.ord_events.append(ord_cancel_req)

    def add_exec_report(self, exec_report):
        if exec_report.ord_id != self.ord_id:
            raise Exception("exec_report [%s] order_id [%s] is not same as current order id [%s]" % (
                exec_report.er_id, exec_report.ord_id, self.ord_id))

        self.exec_events.append(exec_report)
        self.last_price = exec_report.last_price
        self.last_qty = exec_report.last_qty

        avg_price = exec_report.avg_price

        if avg_price:
            self.avg_price = avg_price
        elif self.filled_qty + exec_report.last_qty != 0:
            self.avg_price = ((self.avg_price * self.filled_qty) + (
                self.last_price * self.last_qty)) / (
                                 self.filled_qty + exec_report.last_qty)

        filled_qty = exec_report.filled_qty
        if filled_qty:
            self.filled_qty = filled_qty
        else:
            self.filled_qty += exec_report.last_qty

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

        self.exec_events.append(ord_upd)
        self.status = ord_upd.status

    def get_events(self, type):
        if not type:
            return events
        return [event for event in events if isinstance(event, type)]

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

    def on_ord_update_req(self, order):
        pass

    def on_ord_cancel_req(self, order):
        pass
