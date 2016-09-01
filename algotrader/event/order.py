import copy

from algotrader.event.event import Event


class OrderEvent(Event):
    __slots__ = (
        'ord_id',
        'cl_id',
        'cl_ord_id',
    )

    def __init__(self, timestamp=None, cl_id=None, cl_ord_id=None):
        super(OrderEvent, self).__init__(timestamp)
        self.cl_id = cl_id
        self.cl_ord_id = cl_ord_id


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


class NewOrderRequest(OrderEvent):
    __slots__ = (
        'portf_id',
        'broker_id',
        'inst_id',
        'action',
        'type',
        'qty',
        'limit_price',
        'stop_price',
        'tif',
        'oca_tag',
        'params'
    )

    def __init__(self, timestamp=None, cl_id=None, cl_ord_id=None, portf_id=None, broker_id=None, inst_id=None,
                 action=None, type=None,
                 qty=0, limit_price=0,
                 stop_price=0, tif=TIF.DAY, oca_tag=None, params=None):
        super(NewOrderRequest, self).__init__(timestamp=timestamp, cl_id=cl_id, cl_ord_id=cl_ord_id)
        self.portf_id = portf_id
        self.broker_id = broker_id
        self.inst_id = inst_id
        self.action = action
        self.type = type
        self.qty = qty
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.tif = tif
        self.oca_tag = oca_tag
        self.params = params if params else {}

    def on(self, handler):
        handler.on_new_ord_req(self)

    # def __repr__(self):
    #     return "NewOrderRequest(timestamp = %s, cl_id = %s, cl_ord_id = %s, portf_id = %s, broker_id = %s, inst_id = %s, action = %s" \
    #            ", type = %s, qty = %s, limit_price = %s, stop_price = %s, tif = %s, oca_tag = %s, params = %s)" \
    #            % (self.timestamp, self.cl_id, self.cl_ord_id, self.portf_id, self.broker_id, self.inst_id, self.action,
    #               self.type, self.qty, self.limit_price, self.stop_price, self.tif, self.oca_tag, self.params)

    def is_buy(self):
        return self.action == OrdAction.BUY

    def is_sell(self):
        return self.action == OrdAction.SELL or self.action == OrdAction.SSHORT

    def update_ord_request(self, ord_replace_request):
        new_req = copy.copy(self)

        if ord_replace_request.type:
            new_req.type = ord_replace_request.type
        if ord_replace_request.qty:
            new_req.qty = ord_replace_request.qty
        if ord_replace_request.limit_price:
            new_req.limit_price = ord_replace_request.limit_price
        if ord_replace_request.stop_price:
            new_req.stop_price = ord_replace_request.stop_price
        if ord_replace_request.tif:
            new_req.tif = ord_replace_request.tif
        if ord_replace_request.oca_tag:
            new_req.oca_tag = ord_replace_request.oca_tag
        if ord_replace_request.params:
            new_req.params = ord_replace_request.params

        return new_req


class OrderReplaceRequest(OrderEvent):
    __slots__ = (
        'type',
        'qty',
        'limit_price'
        'stop_price',
        'tif',
        'oca_tag',
        'params'
    )

    def __init__(self, timestamp=None, cl_id=None, cl_ord_id=None, type=None,
                 qty=None, limit_price=None, stop_price=None, tif=None, oca_tag=None, params=None):
        super(OrderReplaceRequest, self).__init__(timestamp=timestamp, cl_id=cl_id, cl_ord_id=cl_ord_id)
        self.type = type
        self.qty = qty
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.tif = tif
        self.oca_tag = oca_tag
        self.params = params if params else {}
    #
    # def __repr__(self):
    #     return "OrderReplaceRequest(timestamp = %s, cl_id = %s, cl_ord_id = %s, " \
    #            ", type = %s, qty = %s, limit_price = %s, stop_price = %s, tif = %s, oca_tag = %s, params = %s)" \
    #            % (self.timestamp, self.cl_id, self.cl_ord_id,
    #               self.type, self.qty, self.limit_price, self.stop_price, self.tif, self.oca_tag, self.params)

    def on(self, handler):
        handler.on_ord_replace_req(self)


class OrderCancelRequest(OrderEvent):
    __slots__ = (
        'params'
    )

    def __init__(self, timestamp=None, cl_id=None, cl_ord_id=None, params=None):
        super(OrderCancelRequest, self).__init__(timestamp=timestamp, cl_id=cl_id, cl_ord_id=cl_ord_id)
        self.params = params if params else {}
    #
    # def __repr__(self):
    #     return "OrderCancelRequest(timestamp = %s, cl_id = %s, cl_ord_id = %s, params = %s)" \
    #            % (self.timestamp, self.cl_id, self.cl_ord_id, self.params)

    def on(self, handler):
        handler.on_ord_cancel_req(self)


class ExecutionEvent(Event):
    __slots__ = (
        'broker_id',
        'ord_id',
        'cl_id',
        'cl_ord_id',
        'inst_id',
    )

    def __init__(self, broker_id=None, ord_id=None, cl_id=None, cl_ord_id=None, inst_id=None, timestamp=None):
        super(ExecutionEvent, self).__init__(timestamp)
        self.broker_id = broker_id
        self.ord_id = ord_id
        self.cl_id = cl_id
        self.cl_ord_id = cl_ord_id
        self.inst_id = inst_id


class OrderStatusUpdate(ExecutionEvent):
    __slots__ = (
        'filled_qty',
        'avg_price',
        'status',

    )

    def __init__(self, broker_id=None, ord_id=None, cl_id=None, cl_ord_id=None, inst_id=None, timestamp=None,
                 filled_qty=0,
                 avg_price=0, status=OrdStatus.NEW):
        super(OrderStatusUpdate, self).__init__(broker_id=broker_id, ord_id=ord_id, cl_id=cl_id, cl_ord_id=cl_ord_id,
                                                inst_id=inst_id, timestamp=timestamp)
        self.filled_qty = filled_qty
        self.avg_price = avg_price
        self.status = status

    def on(self, handler):
        handler.on_ord_upd(self)
    #
    # def __repr__(self):
    #     return "OrderStatusUpdate(broker_id = %s, ord_id = %s, cl_id=%s, cl_ord_id=%s, inst_id = %s, timestamp = %s, status = %s)" \
    #            % (self.broker_id, self.ord_id, self.cl_id, self.cl_ord_id, self.inst_id, self.timestamp, self.status)


class ExecutionReport(OrderStatusUpdate):
    __slots__ = (
        'er_id',
        'last_qty',
        'last_price'
        'commission'
    )

    def __init__(self, broker_id=None, ord_id=None, cl_id=None, cl_ord_id=None, inst_id=None, timestamp=None,
                 er_id=None,
                 last_qty=0, last_price=0,
                 filled_qty=0, avg_price=0, commission=0,
                 status=OrdStatus.NEW):
        super(ExecutionReport, self).__init__(broker_id=broker_id, ord_id=ord_id, cl_id=cl_id, cl_ord_id=cl_ord_id,
                                              inst_id=inst_id,
                                              timestamp=timestamp, filled_qty=filled_qty, avg_price=avg_price,
                                              status=status)
        self.er_id = er_id
        self.last_qty = last_qty
        self.last_price = last_price
        self.commission = commission

    def on(self, handler):
        handler.on_exec_report(self)
    #
    # def __repr__(self):
    #     return "ExecutionReport(broker_id = %s, ord_id = %s, cl_id=%s, cl_ord_id = %s, inst_id = %s, timestamp = %s" \
    #            ", er_id = %s, last_qty = %s, last_price = %s, filled_qty = %s, avg_price = %s, commission = %s)" \
    #            % (self.broker_id, self.ord_id, self.cl_id, self.cl_ord_id, self.inst_id, self.timestamp,
    #               self.er_id, self.last_qty, self.last_price, self.filled_qty, self.avg_price, self.commission)


