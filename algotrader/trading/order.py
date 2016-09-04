from algotrader.event.event_handler import OrderEventHandler, ExecutionEventHandler
from algotrader.event.order import OrdStatus, OrdAction
from algotrader.provider.persistence.persist import Persistable


class Order(OrderEventHandler, ExecutionEventHandler, Persistable):
    __slots__ = (
        'timestamp',
        'cl_id',
        'cl_ord_id',
        'portf_id',
        'broker_id',
        'broker_ord_id',
        'inst_id',
        'action',
        'type',
        'qty',
        'limit_price',
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
        'events'
    )

    def __init__(self, nos=None):
        if nos:
            self.on_new_ord_req(nos)

    def on_new_ord_req(self, nos):
        self.timestamp = nos.timestamp
        self.cl_id = nos.cl_id
        self.cl_ord_id = nos.cl_ord_id
        self.portf_id = nos.portf_id
        self.broker_id = nos.broker_id
        self.broker_ord_id = None
        self.inst_id = nos.inst_id
        self.action = nos.action
        self.type = nos.type
        self.qty = nos.qty
        self.limit_price = nos.limit_price
        self.stop_price = nos.stop_price
        self.tif = nos.tif
        self.oca_tag = nos.oca_tag
        self.params = nos.params
        self.status = OrdStatus.NEW
        self.filled_qty = 0
        self.avg_price = 0
        self.last_qty = 0
        self.last_price = 0
        self.stop_limit_ready = False
        self.trailing_stop_exec_price = 0
        self.events = [nos]

    def on_ord_replace_req(self, ord_replace_req):
        self.events.append(ord_replace_req)

    def on_ord_cancel_req(self, ord_cancel_req):
        self.events.append(ord_cancel_req)

    def on_exec_report(self, exec_report):
        if exec_report.cl_id != self.cl_id or exec_report.cl_ord_id != self.cl_ord_id:
            raise Exception(
                "exec_report [%s] cl_id [%s] cl_ord_id [%s] is not same as current order cl_id [%s] cl_ord_id [%s]" % (
                    exec_report.er_id, exec_report.cl_id, exec_report.cl_ord_id, self.cl_id, self.cl_ord_id))

        if not self.broker_ord_id:
            self.broker_ord_id = exec_report.ord_id
        elif self.broker_ord_id != exec_report.ord_id:
            raise Exception("exec_report [%s] ord_id [%s] is not same as current order ord_id [%s]" % (
                exec_report.er_id, exec_report.ord_id, self.broker_ord_id))

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

        self.events.append(exec_report)

    def on_ord_upd(self, ord_upd):
        if ord_upd.cl_id != self.cl_id or ord_upd.cl_ord_id != self.cl_ord_id:
            raise Exception(
                "ord_upd ord_id [%s] cl_id [%s] cl_ord_id [%s] is not same as current order cl_id [%s] cl_ord_id [%s]" % (
                    ord_upd.ord_id, ord_upd.cl_id, ord_upd.cl_ord_id, self.cl_id, self.cl_ord_id))

        if not self.broker_ord_id:
            self.broker_ord_id = ord_upd.ord_id
        elif self.broker_ord_id != ord_upd.ord_id:
            raise Exception(
                "ord_upd [%s] is not same as current order ord_id [%s]" % (ord_upd.ord_id, self.broker_ord_id))

        self.status = ord_upd.status

        self.events.append(ord_upd)

    def get_events(self, type):
        if not type:
            return self.events
        return [event for event in self.events if isinstance(event, type)]

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
        return self.action == OrdAction.SELL or self.action == OrdAction.SSHORT

    def id(self):
        return "%s.%s" % (self.cl_id, self.cl_ord_id)
