from algotrader import Manager
from algotrader.event.event_bus import EventBus
from algotrader.event.event_handler import MarketDataEventHandler, OrderEventHandler, ExecutionEventHandler
from algotrader.trading.order import Order
from algotrader.utils import logger


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

    def _start(self, app_context, **kwargs):
        self.store = self.app_context.get_trade_data_store()
        self.load_all()
        self.subscriptions = []
        self.subscriptions.append(EventBus.data_subject.subscribe(self.on_next))
        self.subscriptions.append(EventBus.order_subject.subscribe(self.on_next))
        self.subscriptions.append(EventBus.execution_subject.subscribe(self.on_next))

    def _stop(self):
        if self.subscriptions:
            for subscription in self.subscriptions:
                try:
                    subscription.dispose()
                except:
                    pass
        self.save_all()
        self.reset()

    def load_all(self):
        if self.store:
            orders = self.store.load_all('orders')
            for order in orders:
                self.order_dict[order.id()] = order

            new_order_reqs = self.store.load_all('new_order_reqs')
            for new_order_req in new_order_reqs:
                self.ord_reqs_dict[new_order_req.id()] = new_order_req

    def save_all(self):
        if self.store:
            for order in self.order_dict.itervalues():
                self.store.save_order(order)

            for new_order_req in self.ord_reqs_dict.itervalues():
                self.store.save_new_order_req(new_order_req)

    def reset(self):
        self.order_dict = {}
        self.ord_reqs_dict = {}

    def next_ord_id(self):
        return self.app_context.seq_mgr.get_next_sequence(self.id())

    def on_bar(self, bar):
        super(OrderManager, self).on_bar(bar)

    def on_quote(self, quote):
        super(OrderManager, self).on_quote(quote)

    def on_trade(self, trade):
        super(OrderManager, self).on_trade(trade)

    def on_market_depth(self, market_depth):
        super(OrderManager, self).on_market_depth(market_depth)

    def on_ord_upd(self, ord_upd):
        super(OrderManager, self).on_ord_upd(ord_upd)

        # persist
        self.store.save_ord_status_upd(ord_upd)

        # update order
        order = self.order_dict[ord_upd.id()]
        order.on_ord_upd(ord_upd)

        # enrich the cl_id and cl_ord_id
        ord_upd.cl_id = order.cl_id
        ord_upd.cl_ord_id = order.cl_ord_id

        # notify portfolio
        portfolio = self.app_context.portf_mgr.get_portfolio(order.portf_id)
        if portfolio:
            portfolio.on_ord_upd(ord_upd)
        else:
            logger.warn("portfolio [%s] not found for order cl_id [%s] cl_ord_id [%s]" % (
                order.portf_id, order.cl_id, order.cl_ord_id))

        # notify stg
        stg = self.app_context.stg_mgr.get(order.cl_id)
        if stg:
            stg.oon_ord_upd(ord_upd)
        else:
            logger.warn(
                "stg [%s] not found for order cl_id [%s] cl_ord_id [%s]" % (order.cl_id, order.cl_id, order.cl_ord_id))

        # persist
        self.store.save_order(order)

    def on_exec_report(self, exec_report):
        super(OrderManager, self).on_exec_report(exec_report)

        # persist
        self.store.save_exec_report(exec_report)

        # update order
        order = self.order_dict[exec_report.id()]
        order.on_exec_report(exec_report)

        # enrich the cl_id and cl_ord_id
        exec_report.cl_id = order.cl_id
        exec_report.cl_ord_id = order.cl_ord_id

        # notify portfolio
        portfolio = self.app_context.portf_mgr.get_portfolio(order.portf_id)
        if portfolio:
            portfolio.on_exec_report(exec_report)
        else:
            logger.warn("portfolio [%s] not found for order cl_id [%s] cl_ord_id [%s]" % (
                order.portf_id, order.cl_id, order.cl_ord_id))

        # notify stg
        stg = self.app_context.stg_mgr.get(order.cl_id)
        if stg:
            stg.on_exec_report(exec_report)
        else:
            logger.warn(
                "stg [%s] not found for order cl_id [%s] cl_ord_id [%s]" % (order.cl_id, order.cl_id, order.cl_ord_id))

        # persist
        self.store.save_order(order)

    def send_order(self, new_ord_req):
        if new_ord_req.id() in self.order_dict:
            raise Exception(
                "ClientOrderId has been used!! cl_id = %s, cl_ord_id = %s" % (new_ord_req.cl_id, new_ord_req.cl_ord_id))

        # persist
        self.store.save_new_order_req(new_ord_req)

        order = Order(new_ord_req)
        self.order_dict[order.id()] = order

        if order.broker_id:
            broker = self.app_context.provider_mgr.get(order.broker_id)
            if broker:
                broker.on_new_ord_req(new_ord_req)
            else:
                logger.warn("broker [%s] not found for order cl_id [%s] cl_ord_id [%s]" % (
                    order.broker_id, order.cl_id, order.cl_ord_id))

        # persist
        self.store.save_order(order)

        return order

    def cancel_order(self, ord_cancel_req):
        if not ord_cancel_req.id() in self.order_dict:
            raise Exception("ClientOrderId not found!! cl_id = %s, cl_ord_id = %s" % (
                ord_cancel_req.cl_id, ord_cancel_req.cl_ord_id))

        # persist
        self.store.save_ord_cancel_req(ord_cancel_req)

        order = self.order_dict[ord_cancel_req.id()]

        order.on_ord_cancel_req(ord_cancel_req)
        self.app_context.provider_mgr.get(order.broker_id).on_ord_cancel_req(ord_cancel_req)

        # persist
        self.store.save_order(order)

        return order

    def replace_order(self, ord_replace_req):
        if not ord_replace_req.id() in self.order_dict:
            raise Exception("ClientOrderId not found!! cl_id = %s, cl_ord_id = %s" % (
                ord_replace_req.cl_id, ord_replace_req.cl_ord_id))

        # persist
        self.store.save_ord_replace_req(ord_replace_req)

        order = self.order_dict[ord_replace_req.id()]

        order.on_ord_replace_req(ord_replace_req)
        self.app_context.provider_mgr.get(order.broker_id).on_ord_replace_req(ord_replace_req)

        # persist
        self.store.save_order(order)

        return order

    def id(self):
        return "OrderManager"

    def get_portf_orders(self, portf_id):
        return [order for order in self.order_dict.itervalues() if order.portf_id == portf_id]

    def get_strategy_orders(self, stg_id):
        return [order for order in self.order_dict.itervalues() if order.cl_id == stg_id]

    def get_portf_order_reqs(self, portf_id):
        return [new_ord_req for new_ord_req in self.ord_reqs_dict.itervalues() if new_ord_req.portf_id == portf_id]

    def get_strategy_order_reqs(self, stg_id):
        return [new_ord_req for new_ord_req in self.ord_reqs_dict.itervalues() if new_ord_req.cl_id == stg_id]
