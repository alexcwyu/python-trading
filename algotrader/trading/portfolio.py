from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.event.order import OrdAction, OrderEventHandler, ExecutionEventHandler
from algotrader.utils import logger
from algotrader.utils.time_series import TimeSeries


class Position():
    # instrument = Str()
    # orders = Dict(key=Long, value=Order, default={})
    # size = Float()
    # last_price = Float()

    def __init__(self, instrument):
        self.instrument = instrument
        self.orders = {}
        self.size = 0
        self.last_price = 0

    def add_order(self, order):
        if order.instrument != self.instrument:
            raise RuntimeError("order[%s] instrument [%s] is not same as instrument [%s] of position" % (
                order.ord_id, order.instrument, self.instrument))

        if order.ord_id in self.orders:
            raise RuntimeError("order[%s] already exist" % order.ord_id)
        self.orders[order.ord_id] = order
        self.size += order.qty if order.action == OrdAction.BUY else -order.qty

    def filled_qty(self):
        qty = 0
        for key, order in self.orders.iteritems():
            qty += order.filled_qty if order.action == OrdAction.BUY else -order.filled_qty
        return qty

    def __repr__(self):
        return "Position(instrument=%s, orders=%s, size=%s, last_price=%s)" % (
            self.instrument, self.orders, self.size, self.last_price
        )


class Portfolio(OrderEventHandler, ExecutionEventHandler, MarketDataEventHandler):
    # portfolio_id = Str()
    # cash = Float(default=100000)
    # positions = Dict(key=Str, value=Position, default={})
    # orders = Dict(key=Long, value=Order, default={})
    # equity = Value(FloatSeries())

    # pnl = Value(FloatSeries())
    # drawdown = Value(FloatSeries())

    def __init__(self, portfolio_id="test", cash=1000000):
        self.portfolio_id = portfolio_id
        self.cash = cash
        self.positions = {}
        self.orders = {}
        self.stock_mtm_value = TimeSeries()
        self.total_equity = TimeSeries()
        self.pnl = TimeSeries()
        self.drawdown = TimeSeries()

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__update_price(bar.timestamp, bar.instrument, bar.close_or_adj_close())

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__update_price(quote.timestamp, quote.instrument, quote.mid())

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__update_price(trade.timestamp, trade.instrument, trade.price)

    def on_order(self, order):
        logger.debug("[%s] %s" % (self.__class__.__name__, order))

        if order.ord_id in self.orders:
            raise RuntimeError("order[%s] already exist" % order.ord_id)

        self.orders[order.ord_id] = order
        if order.instrument not in self.positions:
            self.positions[order.instrument] = Position(instrument=order.instrument)
        self.positions[order.instrument].add_order(order)

    def on_ord_upd(self, ord_upd):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_upd))
        order = self.orders[ord_upd.ord_id]
        order.update_status(ord_upd)

    def on_exec_report(self, exec_report):
        logger.debug("[%s] %s" % (self.__class__.__name__, exec_report))
        order = self.orders[exec_report.ord_id]
        order.add_exec_report(exec_report)
        direction = 1 if order.action == OrdAction.BUY else -1
        self.cash -= (direction * exec_report.filled_qty * exec_report.filled_price + exec_report.commission)
        self.__update_price(exec_report.timestamp, exec_report.instrument, exec_report.filled_price)

    def __update_price(self, time, instrument, price):
        if instrument in self.positions:
            position = self.positions[instrument]
            position.last_price = price
        self.__update_equity(time)

    def __update_equity(self, time):
        stock_value = 0
        for position in self.positions.itervalues():
            stock_value += position.last_price * position.filled_qty()
        self.stock_mtm_value.add(time, stock_value)
        self.total_equity.add(time, stock_value + self.cash)

    def get_return(self):
        equity = self.total_equity.get_series()
        equity.name = 'equity'
        rets =  equity.pct_change().dropna()
        rets.index = rets.index.tz_localize("UTC")
        return rets