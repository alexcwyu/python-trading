from typing import List, Any

from algotrader import Startable
from algotrader.event.event_handler import MarketDataEventHandler, ExecutionEventHandler
from algotrader.model.model_factory import ModelFactory
from algotrader.model.trade_data_pb2 import *


class Order(MarketDataEventHandler, ExecutionEventHandler, Startable):
    def __init__(self, state: OrderState = None, events: List[Any] = None):
        super().__init__()
        self.__state = state
        self.events = events if events else []

    def _start(self, app_context):
        self.model_factory = app_context.model_factory

    def on_new_ord_req(self, req: NewOrderRequest) -> None:
        if self.__state or len(self.events) > 0:
            raise Exception("NewOrderRequest cannot be added to already initialized order")
        self.__state = self.model_factory.build_order_state_from_nos(req)
        self.events.append(req)

    def on_ord_replace_req(self, req: OrderReplaceRequest) -> None:
        self.events.append(req)

    def on_ord_cancel_req(self, req: OrderCancelRequest) -> None:
        self.events.append(req)

    def on_exec_report(self, exec_report: ExecutionReport) -> None:
        state = self.__state
        if exec_report.broker_id != state.broker_id:
            raise Exception(
                "exec_report [%s] broker_id [%s] is not same as current broker_id [%s]" % (
                    exec_report.er_id, exec_report.broker_id, state.broker_id))

        if exec_report.cl_id != state.cl_id or exec_report.cl_ord_id != state.cl_ord_id:
            raise Exception(
                "exec_report [%s] cl_id [%s] cl_ord_id [%s] is not same as current order cl_id [%s] cl_ord_id [%s]" % (
                    exec_report.er_id, exec_report.cl_id, exec_report.cl_ord_id, state.cl_id, state.cl_ord_id))

        # state.broker_ord_id = exec_report.broker_ord_id
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
            state.status = Filled
        elif state.qty > state.filled_qty:
            state.status = PartiallyFilled
        else:
            raise Exception("filled qty %s is greater than ord qty %s" % (state.filled_qty, state.qty))

        self.events.append(exec_report)

    def on_ord_upd(self, ord_upd: OrderStatusUpdate) -> None:
        state = self.__state

        if ord_upd.broker_id != state.broker_id:
            raise Exception(
                "ord_upd [%s] broker_id [%s] is not same as current broker_id [%s]" % (
                    ord_upd.er_id, ord_upd.broker_id, state.broker_id))

        if ord_upd.cl_id != state.cl_id or ord_upd.cl_ord_id != state.cl_ord_id:
            raise Exception(
                "ord_upd ord_id [%s] cl_id [%s] cl_ord_id [%s] is not same as current order cl_id [%s] cl_ord_id [%s]" % (
                    ord_upd.broker_ord_id, ord_upd.cl_id, ord_upd.cl_ord_id, state.cl_id, state.cl_ord_id))

        if not state.broker_ord_id:
            state.broker_ord_id = ord_upd.broker_ord_id
        elif state.broker_ord_id != ord_upd.broker_ord_id:
            raise Exception(
                "ord_upd [%s] is not same as current order ord_id [%s]" % (ord_upd.broker_ord_id, state.broker_ord_id))

        state.status = ord_upd.status

        self.events.append(ord_upd)

    def get_events(self, type) -> List:
        if not type:
            return self.events
        return [event for event in self.events if isinstance(event, type)]

    def is_buy(self) -> bool:
        if not self.__state:
            return False

        return self.__state.action == Buy

    def is_sell(self) -> bool:
        if not self.__state:
            return False

        return self.__state.action == Sell

    def is_done(self) -> bool:
        if not self.__state:
            return False

        status = self.__state.status
        return status == Rejected or status == Cancelled or status == Filled

    def is_active(self) -> bool:
        if not self.__state:
            return False

        status = self.__state.status
        return status == New or status == PendingSubmit or status == Submitted \
               or status == PartiallyFilled or status == Replaced

    def id(self) -> str:
        return None if not self.__state else ModelFactory.build_cl_ord_id(self.__state.cl_id, self.__state.cl_ord_id)

    def cl_id(self) -> str:
        return None if not self.__state else self.__state.cl_id

    def cl_ord_id(self) -> str:
        return None if not self.__state else self.__state.cl_ord_id

    def portf_id(self) -> str:
        return None if not self.__state else self.__state.portf_id

    def broker_id(self) -> str:
        return None if not self.__state else self.__state.broker_id

    def broker_ord_id(self) -> str:
        return None if not self.__state else self.__state.broker_ord_id

    def inst_id(self) -> str:
        return None if not self.__state else self.__state.inst_id

    def tif(self) -> TIF:
        return None if not self.__state else self.__state.tif

    def action(self) -> OrderAction:
        return None if not self.__state else self.__state.action

    def type(self) -> OrderType:
        return None if not self.__state else self.__state.type

    def status(self) -> OrderStatus:
        return None if not self.__state else self.__state.status

    def qty(self) -> float:
        return None if not self.__state else self.__state.qty

    def limit_price(self) -> float:
        return None if not self.__state else self.__state.limit_price

    def stop_price(self) -> float:
        return None if not self.__state else self.__state.stop_price

    def filled_qty(self) -> float:
        return None if not self.__state else self.__state.filled_qty

    def leave_qty(self) -> float:
        return None if not self.__state else (self.__state.qty - self.__state.filled_qty)

    def avg_price(self) -> float:
        return None if not self.__state else self.__state.avg_price

    def last_qty(self) -> float:
        return None if not self.__state else self.__state.last_qty

    def last_price(self) -> float:
        return None if not self.__state else self.__state.last_price

    def stop_limit_ready(self) -> bool:
        return None if not self.__state else self.__state.stop_limit_ready

    def trailing_stop_exec_price(self) -> float:
        return None if not self.__state else self.__state.trailing_stop_exec_price
