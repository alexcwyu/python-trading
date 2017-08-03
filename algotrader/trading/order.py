from typing import Any
from typing import List

from algotrader import Manager, Startable, Context
from algotrader.model.market_data_pb2 import *
from algotrader.model.model_factory import ModelFactory
from algotrader.model.trade_data_pb2 import *
from algotrader.provider.datastore import PersistenceMode
from algotrader.trading.event import MarketDataEventHandler, OrderEventHandler, ExecutionEventHandler
from algotrader.utils.logging import logger


from algotrader.model.market_data_pb2 import *
from algotrader.model.trade_data_pb2 import *

class Order(MarketDataEventHandler, ExecutionEventHandler, Startable):
    def __init__(self, state: OrderState = None, events: List[Any] = None):
        super().__init__()
        self.state = state
        self.events = events if events else []

    def _start(self, app_context: Context) -> None:
        self.model_factory = app_context.model_factory

    def on_new_ord_req(self, req: NewOrderRequest) -> None:
        if self.state or len(self.events) > 0:
            raise Exception("NewOrderRequest cannot be added to already initialized order")
        self.state = self.model_factory.build_order_state_from_nos(req)
        self.events.append(req)

    def on_ord_replace_req(self, req: OrderReplaceRequest) -> None:
        self.events.append(req)

    def on_ord_cancel_req(self, req: OrderCancelRequest) -> None:
        self.events.append(req)

    def on_exec_report(self, exec_report: ExecutionReport) -> None:
        state = self.state
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
        state = self.state

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
        if not self.state:
            return False

        return self.state.action == Buy

    def is_sell(self) -> bool:
        if not self.state:
            return False

        return self.state.action == Sell

    def is_done(self) -> bool:
        if not self.state:
            return False

        status = self.state.status
        return status == Rejected or status == Cancelled or status == Filled

    def is_active(self) -> bool:
        if not self.state:
            return False

        status = self.state.status
        return status == New or status == PendingSubmit or status == Submitted \
               or status == PartiallyFilled or status == Replaced

    def id(self) -> str:
        return None if not self.state else ModelFactory.build_cl_ord_id(self.state.cl_id, self.state.cl_ord_id)

    def cl_id(self) -> str:
        return None if not self.state else self.state.cl_id

    def cl_ord_id(self) -> str:
        return None if not self.state else self.state.cl_ord_id

    def portf_id(self) -> str:
        return None if not self.state else self.state.portf_id

    def broker_id(self) -> str:
        return None if not self.state else self.state.broker_id

    def broker_ord_id(self) -> str:
        return None if not self.state else self.state.broker_ord_id

    def inst_id(self) -> str:
        return None if not self.state else self.state.inst_id

    def tif(self) -> TIF:
        return None if not self.state else self.state.tif

    def action(self) -> OrderAction:
        return None if not self.state else self.state.action

    def type(self) -> OrderType:
        return None if not self.state else self.state.type

    def status(self) -> OrderStatus:
        return None if not self.state else self.state.status

    def qty(self) -> float:
        return None if not self.state else self.state.qty

    def limit_price(self) -> float:
        return None if not self.state else self.state.limit_price

    def stop_price(self) -> float:
        return None if not self.state else self.state.stop_price

    def filled_qty(self) -> float:
        return None if not self.state else self.state.filled_qty

    def leave_qty(self) -> float:
        return None if not self.state else (self.state.qty - self.state.filled_qty)

    def avg_price(self) -> float:
        return None if not self.state else self.state.avg_price

    def last_qty(self) -> float:
        return None if not self.state else self.state.last_qty

    def last_price(self) -> float:
        return None if not self.state else self.state.last_price

    def stop_limit_ready(self) -> bool:
        return None if not self.state else self.state.stop_limit_ready

    def trailing_stop_exec_price(self) -> float:
        return None if not self.state else self.state.trailing_stop_exec_price


class OrderManager(Manager, OrderEventHandler, ExecutionEventHandler, MarketDataEventHandler):
    __slots__ = (
        'app_context',
        'order_dict',
        'ord_reqs_dict',
    )

    def __init__(self):
        super(OrderManager, self).__init__()
        self.order_dict = {}
        self.ord_reqs_dict = {}
        self.store = None

    def _start(self, app_context: Context) -> None:
        self.store = app_context.get_data_store()
        self.persist_mode = app_context.config.get_app_config("persistenceMode")
        self.load_all()
        self.subscriptions = []
        self.subscriptions.append(app_context.event_bus.data_subject.subscribe(self.on_market_data_event))
        self.subscriptions.append(app_context.event_bus.order_subject.subscribe(self.on_order_event))
        self.subscriptions.append(app_context.event_bus.execution_subject.subscribe(self.on_execution_event))

    def _stop(self):
        if self.subscriptions:
            for subscription in self.subscriptions:
                try:
                    subscription.dispose()
                except:
                    pass
        self.save_all()
        self.reset()

    def all_orders(self):
        return [order for order in self.order_dict.values()]

    def load_all(self):
        if self.store:
            self.store.start(self.app_context)
            order_states = self.store.load_all(OrderState)
            for order_state in order_states:
                order = Order(state=order_state)
                self.order_dict[order.id()] = order

            new_order_reqs = self.store.load_all(NewOrderRequest)
            for new_order_req in new_order_reqs:
                self.ord_reqs_dict[self._cl_ord_id(new_order_req)] = new_order_req

    def save_all(self):
        if self.store and self.persist_mode != PersistenceMode.Disable:
            for order in self.all_orders():
                self.store.save_order(order.state)

            for new_order_req in self.ord_reqs_dict.values():
                self.store.save_new_order_req(new_order_req)

    def reset(self):
        self.order_dict = {}
        self.ord_reqs_dict = {}

    def next_ord_id(self):
        return self.app_context.seq_mgr.get_next_sequence(self.id())

    def on_bar(self, bar: Bar) -> None:
        super(OrderManager, self).on_bar(bar)

    def on_quote(self, quote: Quote) -> None:
        super(OrderManager, self).on_quote(quote)

    def on_trade(self, trade: Trade) -> None:
        super(OrderManager, self).on_trade(trade)

    def on_market_depth(self, market_depth: MarketDepth) -> None:
        super(OrderManager, self).on_market_depth(market_depth)

    def on_ord_upd(self, ord_upd: OrderStatusUpdate) -> None:
        super(OrderManager, self).on_ord_upd(ord_upd)

        # persist
        if self.store and self.persist_mode != PersistenceMode.RealTime:
            self.store.save_ord_status_upd(ord_upd)

        # update order
        order = self.order_dict["%s.%s" % (ord_upd.cl_id, ord_upd.cl_ord_id)]
        order.on_ord_upd(ord_upd)

        # # TODO wtf???
        # # enrich the cl_id and cl_ord_id
        # ord_upd.cl_id = order.cl_id()
        # ord_upd.cl_ord_id = order.cl_ord_id()

        # notify portfolio
        portfolio = self.app_context.portf_mgr.get_portfolio(order.portf_id())
        if portfolio:
            portfolio.on_ord_upd(ord_upd)
        else:
            logger.warn("portfolio [%s] not found for order cl_id [%s] cl_ord_id [%s]" % (
                order.portf_id(), order.cl_id(), order.cl_ord_id()))

        # notify stg
        stg = self.app_context.stg_mgr.get(order.cl_id())
        if stg:
            stg.oon_ord_upd(ord_upd)
        else:
            logger.warn(
                "stg [%s] not found for order cl_id [%s] cl_ord_id [%s]" % (
                    order.cl_id(), order.cl_id(), order.cl_ord_id()))

        # persist
        self._save_order(order)

    def on_exec_report(self, exec_report: ExecutionReport) -> None:
        super(OrderManager, self).on_exec_report(exec_report)

        # persist
        if self.store and self.persist_mode != PersistenceMode.RealTime:
            self.store.save_exec_report(exec_report)

        # update order
        ord_id = self._cl_ord_id(exec_report)
        order = self.order_dict[ord_id]
        order.on_exec_report(exec_report)

        # notify portfolio
        portfolio = self.app_context.portf_mgr.get(order.portf_id())
        if portfolio:
            portfolio.on_exec_report(exec_report)
        else:
            logger.warn("portfolio [%s] not found for order cl_id [%s] cl_ord_id [%s]" % (
                order.portf_id(), order.cl_id(), order.cl_ord_id()))

        # notify stg
        stg = self.app_context.stg_mgr.get(order.cl_id())
        if stg:
            stg.on_exec_report(exec_report)
        else:
            logger.warn(
                "stg [%s] not found for order cl_id [%s] cl_ord_id [%s]" % (
                    order.cl_id(), order.cl_id(), order.cl_ord_id()))

            # persist
            # self._save_order(order)

    def send_order(self, new_ord_req: NewOrderRequest) -> Order:
        ord_id = self._cl_ord_id(new_ord_req)
        if ord_id in self.order_dict:
            raise Exception(
                "ClientOrderId has been used!! ord_id = %s" % (ord_id))

        # persist
        if self.store and self.persist_mode != PersistenceMode.RealTime:
            self.store.save_new_order_req(new_ord_req)

        order = Order(ModelFactory.build_order_state_from_nos(new_ord_req))
        self.order_dict[ord_id] = order

        if order.broker_id():
            broker = self.app_context.provider_mgr.get(order.broker_id())
            if broker:
                broker.on_new_ord_req(new_ord_req)
            else:
                logger.warn("broker [%s] not found for order ord_id [%s]" % (
                    order.broker_id(), ord_id))

        # persist
        # self._save_order(order)

        return order

    def cancel_order(self, ord_cancel_req: OrderCancelRequest) -> Order:
        ord_id = self._cl_ord_id(ord_cancel_req)
        if not ord_id in self.order_dict:
            raise Exception("ClientOrderId not found!! ord_id = %s" % (
                ord_id))

        # persist
        if self.store and self.persist_mode != PersistenceMode.RealTime:
            self.store.save_ord_cancel_req(ord_cancel_req)

        order = self.order_dict[ord_id]

        order.on_ord_cancel_req(ord_cancel_req)
        self.app_context.provider_mgr.get(order.broker_id()).on_ord_cancel_req(ord_cancel_req)

        # persist
        # self._save_order(order)

        return order

    def replace_order(self, ord_replace_req: OrderReplaceRequest) -> Order:
        ord_id = self._cl_ord_id(ord_replace_req)
        if not ord_id in self.order_dict:
            raise Exception("ClientOrderId not found!! ord_id = %s" % (
                ord_id))

        # persist
        if self.store and self.persist_mode != PersistenceMode.RealTime:
            self.store.save_ord_replace_req(ord_replace_req)

        order = self.order_dict[ord_id]

        order.on_ord_replace_req(ord_replace_req)
        self.app_context.provider_mgr.get(order.broker_id()).on_ord_replace_req(ord_replace_req)

        # persist
        self._save_order(order)

        return order

    def id(self) -> str:
        return "OrderManager"

    def get_portf_orders(self, portf_id) -> List[Order]:
        return [order for order in self.order_dict.values() if order.portf_id() == portf_id]

    def get_strategy_orders(self, stg_id) -> List[Order]:
        return [order for order in self.order_dict.values() if order.cl_id() == stg_id]

    def get_portf_order_reqs(self, portf_id) -> List[NewOrderRequest]:
        return [new_ord_req for new_ord_req in self.ord_reqs_dict.values() if new_ord_req.portf_id == portf_id]

    def get_strategy_order_reqs(self, stg_id) -> List[NewOrderRequest]:
        return [new_ord_req for new_ord_req in self.ord_reqs_dict.values() if new_ord_req.cl_id == stg_id]

    def _save_order(self, order):
        if self.store and self.persist_mode != PersistenceMode.RealTime and self.persist_mode != PersistenceMode.Batch:
            self.store.save_order(order.state)

    def _cl_ord_id(self, item):
        return ModelFactory.build_cl_ord_id(item.cl_id, item.cl_ord_id)
