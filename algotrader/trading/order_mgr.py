
from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.event.order import OrderEventHandler, ExecutionEventHandler, Order
from algotrader.provider.provider import broker_mgr
from algotrader.strategy.strategy_mgr import stg_mgr
from algotrader.trading.portfolio_mgr import portf_mgr
from algotrader.utils import logger
from collections import defaultdict

class OrderManager(OrderEventHandler, ExecutionEventHandler, MarketDataEventHandler):
    def __init__(self):
        self.__next_ord_id = 0
        self.__orders = defaultdict(dict)
        self.started = False

    def start(self):
        if not self.started:
            self.started = True
            EventBus.data_subject.subscribe(self.on_next)
            EventBus.order_subject.subscribe(self.on_next)
            EventBus.execution_subject.subscribe(self.on_next)

    def next_ord_id(self):
        next_ord_id = self.__next_ord_id
        self.__next_ord_id += 1
        return next_ord_id

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

        # update order
        order = self.__orders[ord_upd.cl_id][ord_upd.cl_ord_id]
        order.on_ord_upd(ord_upd)

        # enrich the cl_id and cl_ord_id
        ord_upd.cl_id = order.cl_id
        ord_upd.cl_ord_id = order.cl_ord_id

        # notify portfolio
        portfolio = portf_mgr.get_portfolio(order.portf_id)
        if portfolio:
            portfolio.on_ord_upd(ord_upd)
        else:
            logger.warn("portfolio [%s] not found for order cl_id [%s] cl_ord_id [%s]" %(order.portf_id, order.cl_id, order.cl_ord_id))

        # notify stg
        stg = stg_mgr.get_strategy(order.cl_id)
        if stg:
            stg.oon_ord_upd(ord_upd)
        else:
            logger.warn("stg [%s] not found for order cl_id [%s] cl_ord_id [%s]" %(order.cl_id, order.cl_id, order.cl_ord_id))


    def on_exec_report(self, exec_report):
        super(OrderManager, self).on_exec_report(exec_report)

        # update order
        order = self.__orders[exec_report.cl_id][exec_report.cl_ord_id]
        order.on_exec_report(exec_report)

        # enrich the cl_id and cl_ord_id
        exec_report.cl_id = order.cl_id
        exec_report.cl_ord_id = order.cl_ord_id

        # notify portfolio
        portfolio = portf_mgr.get_portfolio(order.portf_id)
        if portfolio:
            portfolio.on_exec_report(exec_report)
        else:
            logger.warn("portfolio [%s] not found for order cl_id [%s] cl_ord_id [%s]" %(order.portf_id, order.cl_id, order.cl_ord_id))

        # notify stg
        stg = stg_mgr.get_strategy(order.cl_id)
        if stg:
            stg.on_exec_report(exec_report)
        else:
            logger.warn("stg [%s] not found for order cl_id [%s] cl_ord_id [%s]" %(order.cl_id, order.cl_id, order.cl_ord_id))


    def send_order(self, new_ord_req):
        if new_ord_req.cl_ord_id in self.__orders[new_ord_req.cl_id]:
            raise Exception(
                "ClientOrderId has been used!! cl_id = %s, cl_ord_id = %s" % (new_ord_req.cl_id, new_ord_req.cl_ord_id))

        order = Order(new_ord_req)
        self.__orders[order.cl_id][order.cl_ord_id] = order
        broker =broker_mgr.get(order.broker_id)
        if broker:
            broker.on_new_ord_req(new_ord_req)
        else:
            logger.warn("broker [%s] not found for order cl_id [%s] cl_ord_id [%s]" %(order.broker_id, order.cl_id, order.cl_ord_id))
        return order

    def cancel_order(self, ord_cancel_req):
        if ord_cancel_req.cl_ord_id not in self.__orders[ord_cancel_req.cl_id]:
            raise Exception("ClientOrderId not found!! cl_id = %s, cl_ord_id = %s" % (
            ord_cancel_req.cl_id, ord_cancel_req.cl_ord_id))

        order = self.__orders[ord_cancel_req.cl_id][ord_cancel_req.cl_ord_id]

        order.on_ord_cancel_req(ord_cancel_req)
        broker_mgr.get(order.broker_id).on_ord_cancel_req(ord_cancel_req)
        return order

    def replace_order(self, ord_replace_req):
        if ord_replace_req.cl_ord_id not in self.__orders[ord_replace_req.cl_id]:
            raise Exception("ClientOrderId not found!! cl_id = %s, cl_ord_id = %s" % (
            ord_replace_req.cl_id, ord_replace_req.cl_ord_id))

        order = self.__orders[ord_replace_req.cl_id][ord_replace_req.cl_ord_id]

        order.on_ord_replace_req(ord_replace_req)
        broker_mgr.get(order.broker_id).on_ord_replace_req(ord_replace_req)
        return order

    def reset(self):
        self.__next_ord_id = 0
        self.__orders = defaultdict(dict)


order_mgr = OrderManager()
