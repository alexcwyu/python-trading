from algotrader.event.event_bus import EventBus
from algotrader.event.event_handler import AccountEventHandler, MarketDataEventHandler, OrderEventHandler, \
    ExecutionEventHandler
from algotrader.event.order import OrdAction
from algotrader.performance.drawdown import DrawDown
from algotrader.performance.returns import Pnl
from algotrader.provider.persistence import Persistable
from algotrader.trading.position import PositionHolder
from algotrader.utils import logger
from algotrader.utils.time_series import DataSeries
from algotrader import Startable, HasId


class Portfolio(PositionHolder, OrderEventHandler, ExecutionEventHandler, MarketDataEventHandler, AccountEventHandler,
                Persistable, Startable):
    __slots__ = (
        'portf_id',
        'ord_reqs',
        'orders',
        'performance_series',
        'total_equity',
        'cash',
        'stock_value',
        'analyzers',
        'started',
    )

    def __init__(self, portf_id="test", cash=1000000, analyzers=None):
        super(Portfolio, self).__init__()
        self.portf_id = portf_id
        self.ord_reqs = {}
        self.orders = {}

        self.performance_series = DataSeries("%s.Performance" % self.portf_id, missing_value=0)
        self.total_equity = 0
        self.cash = cash
        self.stock_value = 0
        self.analyzers = analyzers if analyzers is not None else [Pnl(), DrawDown()]

        for analyzer in self.analyzers:
            analyzer.set_portfolio(self)

        self.started = False
        portf_mgr.add_portfolio(self)

    def start(self):
        if not self.started:
            self.started = True
            order_mgr.start()
            self.__event_subscription = EventBus.data_subject.subscribe(self.on_next)

    def stop(self):
        if self.started:
            self.__event_subscription.dispose()

    def id(self):
        return self.portf_id

    def all_orders(self):
        return [order for cl_orders in self.orders.values() for order in cl_orders.values()]

    def get_order(self, cl_id, cl_ord_id):
        if cl_id not in self.orders:
            return None
        return self.orders[cl_id].get(cl_ord_id, None)

    def on_bar(self, bar):
        super(Portfolio, self).on_bar(bar)
        self.__update_equity(bar.timestamp, bar.inst_id, bar.close)

    def on_quote(self, quote):
        super(Portfolio, self).on_quote(quote)
        self.__update_equity(quote.timestamp, quote.inst_id, quote.mid())

    def on_trade(self, trade):
        super(Portfolio, self).on_trade(trade)
        self.__update_equity(trade.timestamp, trade.inst_id, trade.price)

    def send_order(self, new_ord_req):
        logger.debug("[%s] %s" % (self.__class__.__name__, new_ord_req))

        if new_ord_req.cl_id not in self.ord_reqs:
            self.ord_reqs[new_ord_req.cl_id] = {}

        if new_ord_req.cl_ord_id in self.ord_reqs[new_ord_req.cl_id]:
            raise RuntimeError("ord_reqs[%s][%s] already exist" % (new_ord_req.cl_id, new_ord_req.cl_ord_id))
        self.ord_reqs[new_ord_req.cl_id][new_ord_req.cl_ord_id] = new_ord_req

        order = order_mgr.send_order(new_ord_req)

        if order.cl_id not in self.orders:
            self.orders[order.cl_id] = {}

        self.orders[order.cl_id][order.cl_ord_id] = order
        self.get_position(order.inst_id).add_order(order)
        return order

    def cancel_order(self, ord_cancel_req):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_cancel_req))
        order = order_mgr.cancel_order(ord_cancel_req)
        return order

    def replace_order(self, ord_replace_req):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_replace_req))
        order = order_mgr.replace_order(ord_replace_req)
        return order

    def on_new_ord_req(self, new_ord_req):
        if new_ord_req.portf_id == self.portf_id:
            self.send_order(new_ord_req)

    def on_ord_cancel_req(self, ord_cancel_req):
        if ord_cancel_req.portf_id == self.portf_id:
            self.cancel_order(ord_cancel_req)

    def on_ord_replace_req(self, ord_replace_req):
        if ord_replace_req.portf_id == self.portf_id:
            self.replace_order(ord_replace_req)

    def on_ord_upd(self, ord_upd):
        if ord_upd.portf_id == self.portf_id:
            logger.debug("[%s] %s" % (self.__class__.__name__, ord_upd))

    def on_exec_report(self, exec_report):
        logger.debug("[%s] %s" % (self.__class__.__name__, exec_report))

        if exec_report.cl_id not in self.ord_reqs and exec_report.cl_ord_id not in self.ord_reqs[exec_report.cl_id]:
            raise Exception("Order not found, ord_reqs[%s][%s]" % (exec_report.cl_id, exec_report.cl_ord_id))

        new_ord_req = self.ord_reqs[exec_report.cl_id][exec_report.cl_ord_id]
        direction = 1 if new_ord_req.action == OrdAction.BUY else -1
        if exec_report.last_qty > 0:
            self.cash -= (direction * exec_report.last_qty * exec_report.last_price + exec_report.commission)
            self.add_position(exec_report.inst_id, exec_report.cl_id, exec_report.cl_ord_id,
                              direction * exec_report.last_qty)
            self.update_position_price(exec_report.timestamp, exec_report.inst_id, exec_report.last_price)

    def update_position_price(self, timestamp, inst_id, price):
        super(Portfolio, self).update_position_price(timestamp, inst_id, price)
        self.__update_equity(timestamp, inst_id, price)
        for analyzer in self.analyzers:
            analyzer.update(timestamp)

    def __update_equity(self, time, inst_id, price):
        self.stock_value = 0
        for position in self.positions.itervalues():
            self.stock_value += position.current_value()
        self.total_equity = self.stock_value + self.cash

        self.performance_series.add(
            {"timestamp": time, "stock_value": self.stock_value, "cash": self.cash, "total_equity": self.total_equity})

    def get_return(self):
        equity = self.performance_series.get_series("total_equity")
        equity.name = 'equity'
        rets = equity.pct_change().dropna()
        # rets.index = rets.index.tz_localize("UTC")
        return rets

    def get_series(self):
        result = self.performance_series.get_series(['stock_value', 'cash', 'total_equity'])

        for analyzer in self.analyzers:
            result.update(analyzer.get_series())
        return result

    def get_result(self):
        result = {
            "TotalEquity": self.total_equity,
            "Cash": self.cash,
            "StockValue": self.stock_value
        }

        for analyzer in self.analyzers:
            result.update(analyzer.get_result())
        return result

    def on_acc_upd(self, acc_upd):
        pass

    def on_portf_upd(self, portf_upd):
        # TODO
        pass
