import datetime

from atom.api import Atom, Str, Value, Float, Long, Dict, Int

from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.event.order import Order, OrdAction, OrderEventHandler, ExecutionEventHandler
from algotrader.tools import *
from collections import defaultdict
import numpy as np

class Position():
    # instrument = Str()
    # orders = Dict(key=Long, value=Order, default={})
    # size = Float()
    # last_price = Float()

    def __init__(self, instrument):
        self.instrument = instrument
        self.orders = {}
        self.size =0
        self.last_price = 0

    def add_order(self, order):
        if order.ord_id in self.orders:
            raise RuntimeError("order[%s] already exist" % order.ord_id)
        self.orders[order.ord_id] = order
        self.size += order.qty if order.action == OrdAction.BUY else -order.qty

    def filled_qty(self):
        qty = 0
        for key, order in self.orders:
            qty += order.filled_qty if order.action == OrdAction.Buy else -order.filled_qty
        return qty

    def __repr__(self):
        return "Position(instrument=%s, orders=%s, size=%s, last_price=%s)"%(
            self.instrument, self.orders, self.size, self.last_price
        )



class FloatSeries(Atom):
    time = Value(np.empty([0], dtype='datetime64'))
    value = Value(np.empty([0], dtype='float'))
    lenght = Int(0)

    def add(self, time, value):
        self.time = np.append(self.time, time)
        self.value = np.append(self.value, value)
        self.lenght += 1

    def get_time_value(self):
        return (self.time, self.value)

    def get_time_value_as_series(self):
        return pd.Series(data=self.value, index=self.time)

    def size(self):
        return self.lenght


class Portfolio(OrderEventHandler, ExecutionEventHandler, MarketDataEventHandler):
    # portfolio_id = Str()
    # cash = Float(default=100000)
    # positions = Dict(key=Str, value=Position, default={})
    # orders = Dict(key=Long, value=Order, default={})
    # equity = Value(FloatSeries())
    # pnl = Value(FloatSeries())
    # drawdown = Value(FloatSeries())

    def __init__(self, portfolio_id = "test", cash = 100000):
        self.portfolio_id = portfolio_id
        self.cash = cash
        self.positions = {}
        self.orders = {}
        self.equity=FloatSeries()

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.update_price(bar.timestamp, bar.instrument, bar.close_or_adj_close())

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.update_price(quote.timestamp, quote.instrument, quote.mid())

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.update_price(trade.timestamp, trade.instrument, trade.price)

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

    def update_price(self, time, instrument, price):
        if instrument in self.positions:
            position = self.positions[instrument]
            position.last_price = price
        self.update_equity(time)

    def update_equity(self, time):
        value = self.cash
        for position in self.positions.itervalues():
            value += position.last_price * position.filled_qty()
        self.equity.add(time, value)


if __name__ == "__main__":
    # order = Order(instrument="HSI", timestamp=datetime.datetime.now(), ord_id=1,
    #               stg_id="SMA", broker_id="SIMULATOR", type=OrdType.LIMIT, tif=TIF.DAY, qty=10000,
    #               limit_price=18888)
    #
    # exec_report1 = ExecutionReport(instrument="HSI",
    #                                timestamp=datetime.datetime.now(), ord_id=1,
    #                                broker_id="SIMULATOR", er_id=20, filled_qty=2000, filled_price=18887)
    #
    # exec_report2 = ExecutionReport(instrument="HSI",
    #                                timestamp=datetime.datetime.now(), ord_id=1,
    #                                broker_id="SIMULATOR", er_id=21, filled_qty=4000, filled_price=18880)
    #
    # order.add_exec_report(exec_report1)
    # order.add_exec_report(exec_report2)
    #
    # print order

    import pandas as pd
    import numpy as np

    x = pd.Series(dtype=float, )

    time = np.empty([0], dtype='datetime64')
    time = np.append(time, datetime.datetime.now())
    time = np.append(time, datetime.datetime.now())

    series = FloatSeries()
    series2 = FloatSeries()
    series.add(datetime.datetime.now(), 61)
    series.add(datetime.datetime.now(), 62)
    print series.get_time_value_as_series()

    p = Portfolio()
    print p.cash
