from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from builtins import *


from algotrader.event.event_bus import EventBus
from algotrader.model.trade_data_pb2 import *
from algotrader.model.trading.position import HasPositions
from algotrader.utils import logger
from algotrader.model.trading.analyzer.performance import PerformanceAnalyzer
from algotrader.model.trading.analyzer.pnl import PnlAnalyzer
from algotrader.model.trading.analyzer.drawdown import DrawDownAnalyzer


class Portfolio(HasPositions):
    def __init__(self, state: PortfolioState = None, model_factory = None):
        super().__init__()
        self.state = state
        self.performance = PerformanceAnalyzer(self)
        self.pnl = PnlAnalyzer(self)
        self.drawdown = DrawDownAnalyzer(self)
        self.model_factory = model_factory
        self.ord_reqs = {}

    def _start(self, app_context, **kwargs):
        self.app_context.portf_mgr.add(self)
        self.model_factory = app_context.model_factory

        self.event_subscription = EventBus.data_subject.subscribe(self.on_next)

        for order_req in self.app_context.order_mgr.get_portf_order_reqs(self.id()):
            self.ord_reqs[self.model_factory.build_client_order_id(cl_id=order_req.cl_id,
                                                                   cl_req_id=order_req.cl_req_id)] = order_req

    def _stop(self):
        self.event_subscription.dispose()

    def id(self):
        return self.portf_id

    def on_bar(self, bar):
        super(Portfolio, self).on_bar(bar)
        self.__update_equity(bar.timestamp, bar.inst_id, bar.close)

    def on_quote(self, quote):
        super(Portfolio, self).on_quote(quote)
        self.__update_equity(quote.timestamp, quote.inst_id, quote.mid())

    def on_trade(self, trade):
        super(Portfolio, self).on_trade(trade)
        self.__update_equity(trade.timestamp, trade.inst_id, trade.price)

    def send_order(self, req: NewOrderRequest) -> None:
        logger.debug("[%s] %s" % (self.__class__.__name__, req))

        # TODO check
        # if new_ord_req.cl_id in self.ord_reqs and new_ord_req.cl_ord_id in self.ord_reqs[new_ord_req.cl_id]:
        #     raise RuntimeError("ord_reqs[%s][%s] already exist" % (new_ord_req.cl_id, new_ord_req.cl_ord_id))

        self.ord_reqs[self.model_factory.build_client_order_id_str(cl_id=req.cl_id, cl_req_id=req.cl_req_id)] = req
        self.add_order(inst_id=req.inst_id, cl_id=req.cl_id, cl_req_id=req.cl_req_id,
                       ordered_qty=req.qty)
        self.app_context.order_mgr.send_order(req)

    def cancel_order(self, req: OrderCancelRequest) -> None:
        logger.debug("[%s] %s" % (self.__class__.__name__, req))
        self.ord_reqs[self.model_factory.build_client_order_id_str(cl_id=req.cl_id, cl_req_id=req.cl_req_id)] = req
        self.app_context.order_mgr.cancel_order(req)

    def replace_order(self, req: OrderReplaceRequest) -> None:
        logger.debug("[%s] %s" % (self.__class__.__name__, req))
        self.ord_reqs[self.model_factory.build_client_order_id_str(cl_id=req.cl_id, cl_req_id=req.cl_req_id)] = req
        self.app_context.order_mgr.replace_order(req)

    def on_new_ord_req(self, req):
        if req.portf_id == self.portf_id:
            self.send_order(req)

    def on_ord_cancel_req(self, req):
        if req.portf_id == self.portf_id:
            self.cancel_order(req)

    def on_ord_replace_req(self, req):
        if req.portf_id == self.portf_id:
            self.replace_order(req)

    def on_ord_upd(self, ord_upd):
        if ord_upd.portf_id == self.portf_id:
            logger.debug("[%s] %s" % (self.__class__.__name__, ord_upd))

    def on_exec_report(self, exec_report):
        logger.debug("[%s] %s" % (self.__class__.__name__, exec_report))

        # TODO check
        # if exec_report.cl_id not in self.ord_reqs and exec_report.cl_ord_id not in self.ord_reqs[exec_report.cl_id]:
        #     raise Exception("Order not found, ord_reqs[%s][%s]" % (exec_report.cl_id, exec_report.cl_ord_id))

        new_ord_req = self.ord_reqs[
            self.model_factory.build_client_order_id_str(cl_id=exec_report.cl_id, cl_req_id=exec_report.cl_req_id)]

        if not new_ord_req:
            raise Exception("request not found")
        direction = 1 if new_ord_req.action == OrderAction.BUY else -1
        if exec_report.last_qty > 0:
            self.cash -= (direction * exec_report.last_qty * exec_report.last_price + exec_report.commission)
            self.add_position(exec_report.inst_id, exec_report.cl_id, exec_report.cl_req_id,
                              direction * exec_report.last_qty)
            self.update_position_price(exec_report.timestamp, exec_report.inst_id, exec_report.last_price)

    def update_position_price(self, timestamp: int, inst_id: str, price: float) -> None:
        super(Portfolio, self).update_position_price(timestamp, inst_id, price)
        self.__update_equity(timestamp, inst_id, price)
        for analyzer in self.analyzers:
            analyzer.update(timestamp)

    def __update_equity(self, timestamp: int, inst_id: str, price: float) -> None:
        self.stock_value = self.total_value()
        self.total_equity = self.stock_value + self.cash

    def get_return(self):
        equity = self.performance.get_series("total_equity")
        equity.name = 'equity'
        rets = equity.pct_change().dropna()
        # rets.index = rets.index.tz_localize("UTC")
        return rets

    def get_series(self):
        result = self.performance.get_series(['stock_value', 'cash', 'total_equity'])

        for analyzer in self.analyzers:
            result.update(analyzer.get_series())
        return result

    def get_result(self):
        result = {}
        for analyzer in self.analyzers:
            result.update(analyzer.get_result())
        return result

    def on_acc_upd(self, acc_upd):
        pass

    def on_portf_upd(self, portf_upd):
        # TODO
        pass

