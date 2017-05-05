from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from builtins import *
from typing import Dict

from algotrader import Startable, HasId
from algotrader.model.trade_data_pb2 import *
from algotrader.trading.analyzer.drawdown import DrawDownAnalyzer
from algotrader.trading.analyzer.performance import PerformanceAnalyzer
from algotrader.trading.analyzer.pnl import PnlAnalyzer
from algotrader.trading.position import HasPositions
from algotrader.utils import logger


class Portfolio(HasPositions, Startable, HasId):
    def __init__(self, state: PortfolioState = None):
        super().__init__(state)
        self.__state = state
        self.performance = PerformanceAnalyzer(self, state)
        self.pnl = PnlAnalyzer(self, state)
        self.drawdown = DrawDownAnalyzer(self, state)
        self.__analyzers = [self.performance, self.pnl, self.drawdown]
        self.__ord_reqs = {}

    def _start(self, app_context) -> None:
        self.app_context.portf_mgr.add(self)

        self.event_subscription = app_context.event_bus.data_subject.subscribe(self.on_market_data_event)

        for order_req in self.app_context.order_mgr.get_portf_order_reqs(self.id()):
            self.__ord_reqs[order_req.cl_ord_id] = order_req

    def _stop(self) -> None:
        self.event_subscription.dispose()

    def id(self) -> str:
        return self.__state.portf_id

    # def on_bar(self, bar):
    #     super(Portfolio, self).on_bar(bar)
    #     self.__update_equity(bar.timestamp, bar.inst_id, bar.close)
    #
    # def on_quote(self, quote):
    #     super(Portfolio, self).on_quote(quote)
    #     self.__update_equity(quote.timestamp, quote.inst_id, quote.mid())
    #
    # def on_trade(self, trade):
    #     super(Portfolio, self).on_trade(trade)
    #     self.__update_equity(trade.timestamp, trade.inst_id, trade.price)

    def send_order(self, req: NewOrderRequest) -> None:
        logger.debug("[%s] %s" % (self.__class__.__name__, req))

        self.__ord_reqs[req.cl_ord_id] = req
        self.add_order(inst_id=req.inst_id, cl_id=req.cl_id, cl_ord_id=req.cl_ord_id,
                       ordered_qty=req.qty if req.action == Buy else -req.qty)
        return self.app_context.order_mgr.send_order(req)

    def cancel_order(self, req: OrderCancelRequest) -> None:
        logger.debug("[%s] %s" % (self.__class__.__name__, req))
        self.__ord_reqs[req.cl_ord_id] = req
        return self.app_context.order_mgr.cancel_order(req)

    def replace_order(self, req: OrderReplaceRequest) -> None:
        logger.debug("[%s] %s" % (self.__class__.__name__, req))
        self.__ord_reqs[req.cl_ord_id] = req
        return self.app_context.order_mgr.replace_order(req)

    def on_new_ord_req(self, req: NewOrderRequest) -> None:
        if req.portf_id == self.__state.portf_id:
            self.send_order(req)

    def on_ord_cancel_req(self, req: OrderCancelRequest) -> None:
        if req.portf_id == self.__state.portf_id:
            self.cancel_order(req)

    def on_ord_replace_req(self, req: OrderReplaceRequest) -> None:
        if req.portf_id == self.__state.portf_id:
            self.replace_order(req)

    def on_ord_upd(self, ord_upd: OrderStatusUpdate) -> None:
        if ord_upd.portf_id == self.__state.portf_id:
            logger.debug("[%s] %s" % (self.__class__.__name__, ord_upd))

    def on_exec_report(self, exec_report: ExecutionReport) -> None:
        logger.debug("[%s] %s" % (self.__class__.__name__, exec_report))

        new_ord_req = self.__ord_reqs[exec_report.cl_ord_id]

        if not new_ord_req:
            raise Exception("request not found")
        direction = 1 if new_ord_req.action == Buy else -1
        if exec_report.last_qty > 0:
            self.__state.cash -= (direction * exec_report.last_qty * exec_report.last_price + exec_report.commission)
            self.add_position(exec_report.inst_id, exec_report.cl_id, exec_report.cl_ord_id,
                              direction * exec_report.last_qty)
            self.update_price(exec_report.timestamp, exec_report.inst_id, exec_report.last_price)

    def update_price(self, timestamp: int, inst_id: str, price: float) -> None:
        super().update_price(timestamp, inst_id, price)
        self.__update_equity(timestamp, inst_id, price)
        for analyzer in self.__analyzers:
            analyzer.update(timestamp, self.total_equity)

    def __update_equity(self, timestamp: int, inst_id: str, price: float) -> None:
        self.__state.stock_value = self.total_position_value()
        self.total_equity = self.__state.stock_value + self.__state.cash

    def get_return(self) -> float:
        equity = self.performance.get_series("total_equity")
        equity.name = 'equity'
        rets = equity.pct_change().dropna()
        # rets.index = rets.index.tz_localize("UTC")
        return rets

    def get_series(self):
        result = self.performance.get_series(['stock_value', 'cash', 'total_equity'])

        for analyzer in self.__analyzers:
            result.update(analyzer.get_series())
        return result

    def get_result(self) -> Dict[str, float]:
        result = {}
        for analyzer in self.__analyzers:
            result.update(analyzer.get_result())
        return result

    def on_acc_upd(self, acc_upd) -> None:
        pass

    def on_portf_upd(self, portf_upd) -> None:
        # TODO
        pass

    def cash(self) -> float:
        if not self.__state:
            return None
        return self.__state.cash

    def stock_value(self) -> float:
        if not self.__state:
            return None
        return self.__state.stock_value

    def performance(self) -> PerformanceAnalyzer:
        return self.performance

    def pnl(self) -> PnlAnalyzer:
        return self.pnl

    def drawdown(self) -> DrawDownAnalyzer:
        return self.drawdown

    def ord_reqs(self):
        return self.__ord_reqs
