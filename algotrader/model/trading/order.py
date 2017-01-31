from typing import List, Any

from algotrader.model.model_factory import ModelFactory
from algotrader.model.trade_data_pb2 import *


class Order(object):
    def __init__(self, state: OrderState = None, events: List[Any] = None):
        self.state = state
        self.events = events if events else []

    def _start(self, app_context, **kwargs):
        self.model_factory = app_context.model_factory

    def on_new_ord_req(self, req: NewOrderRequest):
        if self.state or len(self.events) > 0:
            raise Exception("NewOrderRequest cannot be added to already initialized order")
        self.state = self.model_factory.build_order_state_from_nos(req)
        self.events.append(req)

    def on_ord_replace_req(self, req: OrderReplaceRequest):
        self.events.append(req)

    def on_ord_cancel_req(self, req: OrderCancelRequest):
        self.events.append(req)

    def on_exec_report(self, exec_report: ExecutionReport):
        state = self.state
        if exec_report.broker_id != state.broker_id:
            raise Exception(
                "exec_report [%s] broker_id [%s] is not same as current broker_id [%s]" % (
                    exec_report.er_id, exec_report.broker_id, state.broker_id))

        if exec_report.cl_id != state.cl_id or exec_report.cl_req_id != state.cl_req_id:
            raise Exception(
                "exec_report [%s] cl_id [%s] cl_req_id [%s] is not same as current order cl_id [%s] cl_req_id [%s]" % (
                    exec_report.er_id, exec_report.cl_id, exec_report.cl_req_id, state.cl_id, state.cl_req_id))

        if not state.broker_ord_id:
            state.broker_ord_id = exec_report.broker_ord_id
        elif state.broker_ord_id != exec_report.broker_ord_id:
            raise Exception("exec_report [%s] ord_id [%s] is not same as current order ord_id [%s]" % (
                exec_report.er_id, exec_report.broker_ord_id, state.broker_ord_id))

        state.last_price = exec_report.last_price
        state.last_qty = exec_report.last_qty

        avg_price = exec_report.avg_price

        if avg_price:
            state.avg_price = avg_price
        elif state.filled_qty + exec_report.last_qty != 0:
            state.avg_price = ((state.avg_price * state.filled_qty) + (
                state.last_price * state.last_qty)) / (
                                  state.filled_qty + exec_report.last_qty)

        filled_qty = exec_report.filled_qty
        if filled_qty:
            state.filled_qty = filled_qty
        else:
            state.filled_qty += exec_report.last_qty

        if state.qty == state.filled_qty:
            state.status = OrderStatus.FILLED
        elif state.qty > state.filled_qty:
            state.status = OrderStatus.PARTIALLY_FILLED
        else:
            raise Exception("filled qty %s is greater than ord qty %s" % (state.filled_qty, state.qty))

        self.events.append(exec_report)

    def on_ord_upd(self, ord_upd):
        state = self.state

        if ord_upd.broker_id != state.broker_id:
            raise Exception(
                "ord_upd [%s] broker_id [%s] is not same as current broker_id [%s]" % (
                    ord_upd.er_id, ord_upd.broker_id, state.broker_id))

        if ord_upd.cl_id != state.cl_id or ord_upd.cl_ord_id != state.cl_ord_id:
            raise Exception(
                "ord_upd ord_id [%s] cl_id [%s] cl_ord_id [%s] is not same as current order cl_id [%s] cl_ord_id [%s]" % (
                    ord_upd.ord_id, ord_upd.cl_id, ord_upd.cl_ord_id, state.cl_id, state.cl_ord_id))

        if not state.broker_ord_id:
            state.broker_ord_id = ord_upd.ord_id
        elif state.broker_ord_id != ord_upd.ord_id:
            raise Exception(
                "ord_upd [%s] is not same as current order ord_id [%s]" % (ord_upd.ord_id, state.broker_ord_id))

        state.status = ord_upd.status

        self.events.append(ord_upd)

    def get_events(self, type):
        if not type:
            return self.events
        return [event for event in self.events if isinstance(event, type)]

    def is_done(self):
        status = self.state.status
        return status == OrderStatus.REJECTED or status == OrderStatus.CANCELLED or status == OrderStatus.FILLED

    def is_active(self):
        status = self.state.status
        return status == OrderStatus.NEW or status == OrderStatus.PENDING_SUBMIT or status == OrderStatus.SUBMITTED \
               or status == OrderStatus.PARTIALLY_FILLED or status == OrderStatus.REPLACED

    def leave_qty(self):
        return self.state.qty - self.state.filled_qty

    def is_buy(self):
        return self.state.action == OrderAction.BUY

    def is_sell(self):
        return self.state.action == OrderAction.SELL or self.state.action == OrderAction.SSHORT