import abc

from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import Bar, Trade, Quote
from algotrader.event.order import MarketDataEventHandler, OrderEventHandler, OrdType, OrdStatus, ExecutionReport, \
    OrdAction
from algotrader.provider import Provider
from algotrader.tools import *
from algotrader.trading.clock import clock
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.trading.order_mgr import order_mgr


# from algotrader.tools import *


class Broker(Provider, OrderEventHandler):
    __metaclass__ = abc.ABCMeta

    def start(self):
        pass


class SimOrderHandler:
    __metaclass__ = abc.ABCMeta

    def __init__(self, simulator):
        self.__simulator = simulator

    def process(self, event):
        if isinstance(event, Bar):
            return self.process_w_bar(event)
        elif isinstance(event, Quote):
            return self.process_w_quote(event)
        elif isinstance(event, Trade):
            return self.process_w_trade(event)

    @abc.abstractmethod
    def process_w_quote(self, order, quote):
        pass

    @abc.abstractmethod
    def process_w_trade(self, order, trade):
        pass

    @abc.abstractmethod
    def process_w_bar(self, order, bar):
        pass

    @abc.abstractmethod
    def process_w_price_qty(self, order, price, qty):
        pass


class MarketOrderHandler(SimOrderHandler):
    def __init__(self, simulator):
        super(self.__class__, self).__init__(simulator)

    def process_w_bar(self, order, bar):
        return False

    def process_w_trade(self, order, trade):
        return False

    def process_w_quote(self, order, quote):
        return False

    def process_w_price_qty(self, order, price, qty):
        return False


class LimitOrderHandler(SimOrderHandler):
    def __init__(self, simulator):
        super(self.__class__, self).__init__(simulator)

    def process_w_bar(self, order, bar):
        return False

    def process_w_trade(self, order, trade):
        return False

    def process_w_quote(self, order, quote):
        return False

    def process_w_price_qty(self, order, price, qty):
        return False


class StopLimitOrderHandler(SimOrderHandler):
    def __init__(self, simulator):
        super(self.__class__, self).__init__(simulator)

    def process_w_bar(self, order, bar):
        return False

    def process_w_trade(self, order, trade):
        return False

    def process_w_quote(self, order, quote):
        return False

    def process_w_price_qty(self, order, price, qty):
        return False


class StopOrderHandler(SimOrderHandler):
    def __init__(self, simulator):
        super(self.__class__, self).__init__(simulator)

    def process_w_bar(self, order, bar):
        return False

    def process_w_trade(self, order, trade):
        return False

    def process_w_quote(self, order, quote):
        return False

    def process_w_price_qty(self, order, price, qty):
        return False


class TrailingStopOrderHandler(SimOrderHandler):
    def __init__(self, simulator):
        super(self.__class__, self).__init__(simulator)

    def process_w_bar(self, order, bar):
        return False

    def process_w_trade(self, order, trade):
        return False

    def process_w_quote(self, order, quote):
        return False

    def process_w_price_qty(self, order, price, qty):
        return False


class SimConfig:
    class FillMode:
        LAST = 0
        NEXT_OPEN = 1
        NEXT_CLOSE = 1

    def __init__(self, fill_on_quote=True,
                 fill_on_trade=True,
                 fill_on_bar=True,
                 fill_on_quote_mode=FillMode.LAST,
                 fill_on_trade_mode=FillMode.LAST,
                 fill_on_bar_mode=FillMode.LAST):
        self.fill_on_quote = fill_on_quote
        self.fill_on_trade = fill_on_trade
        self.fill_on_bar = fill_on_bar
        self.fill_on_quote_mode = fill_on_quote_mode
        self.fill_on_trade_mode = fill_on_trade_mode
        self.fill_on_bar_mode = fill_on_bar_mode


@singleton
class Simulator(Broker, MarketDataEventHandler):
    ID = "Simulator"

    def __init__(self, sim_config=None):
        self.__next_exec_id = 0
        self.__order_map = {}
        self.__quote_map = {}
        self.__sim_config = sim_config if sim_config else SimConfig()
        self.__market_ord_handler = MarketOrderHandler(self)
        self.__limit_ord_handler = LimitOrderHandler(self)
        self.__stop_limit_ord_handler = StopLimitOrderHandler(self)
        self.__stop_ord_handler = StopOrderHandler(self)
        self.__trailing_stop_ord_handler = TrailingStopOrderHandler(self)

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def stop(self):
        pass

    def next_exec_id(self):
        __next_exec_id = self.__next_exec_id
        self.__next_exec_id += 1
        return __next_exec_id

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        if self.__sim_config.fill_on_bar and bar.instrument in self.__order_map:
            for order in self.__order_map[bar.instrument].itervalues():
                executed = False
                if self.__sim_config.fill_on_bar_mode == SimConfig.FillMode.NEXT_OPEN:
                    executed = self.__process_w_price_qty(order, bar.open, order.qty)

                if not executed:
                    executed = self.__process(order, bar)

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))

        diff_ask = True
        diff_bid = True

        if quote.instrument in self.__quote_map:
            prev_quote = self.__quote_map[quote.instrument]
            diff_ask = prev_quote.ask != quote.ask or prev_quote.ask_size != quote.ask_size
            diff_bid = prev_quote.bid != quote.bid or prev_quote.bid_size != quote.bid_size

        self.__quote_map[quote.instrument] = quote

        if self.__sim_config.fill_on_quote and quote.instrument in self.__order_map:
            for order in self.__order_map[quote.instrument].itervalues():
                if order.action == OrdAction.BUY and diff_ask:
                    self.__process(order, quote)
                elif order.action == OrdAction.SELL and diff_bid:
                    self.__process(order, quote)

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        if self.__sim_config.fill_on_trade and trade.instrument in self.__order_map:
            for order in self.__order_map[trade.instrument].itervalues():
                self.__process(order, trade)

    def on_order(self, order):
        logger.debug("[%s] %s" % (self.__class__.__name__, order))

        self.__add_order(order)
        self.__send_exec_report(order, 0, 0, OrdStatus.SUBMITTED)
        if self.__process_new_order(order):
            self.__remove_order(order)

    def __add_order(self, order):
        orders = self.__order_map.get(order.instrument, {})
        orders[order.ord_id] = order

    def __remove_order(self, order):
        if order.instrument in self.__order_map:
            orders = self.__order_map[order.instrument]
            if order.ord_id in orders:
                del orders[order.ord_id]

    def __process_new_order(self, order):
        executed = False
        config = self.__sim_config

        quote = inst_data_mgr.get_quote(order.instrument)
        trade = inst_data_mgr.get_trade(order.instrument)
        bar = inst_data_mgr.get_bar(order.instrument)

        if order.type == OrdType.MARKET:
            if not executed and config.fill_on_quote and config.fill_on_bar_mode == SimConfig.FillMode.LAST and quote:
                executed = self.__market_ord_handler.process_w_quote(order, quote)
            if not executed and config.fill_on_trade and config.fill_on_trade_mode == SimConfig.FillMode.LAST and trade:
                executed = self.__market_ord_handler.process_w_trade(order, trade)
            if not executed and config.fill_on_bar and config.fill_on_bar_mode == SimConfig.FillMode.LAST and bar:
                executed = self.__market_ord_handler.process_w_bar(order, bar)
        else:
            if not executed and config.fill_on_quote and quote:
                executed = self.__process(order, quote)
            if not executed and config.fill_on_trade and trade:
                executed = self.__process(order, trade)
            if not executed and config.fill_on_bar and bar:
                executed = self.__process(order, bar)

        return executed

    def __process(self, order, event):
        if order.type == OrdType.MARKET:
            return self.__market_ord_handler.process(order, event)
        elif order.type == OrdType.LIMIT:
            return self.__limit_ord_handler.process(order, event)
        elif order.type == OrdType.STOP_LIMIT:
            return self.__stop_limit_ord_handler.process(order, event)
        elif order.type == OrdType.STOP:
            return self.__stop_ord_handler.process(order, event)
        return False

    def __process_w_price_qty(self, order, price, qty):
        if order.type == OrdType.MARKET:
            return self.__market_ord_handler.process(order, price, qty)
        elif order.type == OrdType.LIMIT:
            return self.__limit_ord_handler.process(order, price, qty)
        elif order.type == OrdType.STOP_LIMIT:
            return self.__stop_limit_ord_handler.process(order, price, qty)
        elif order.type == OrdType.STOP:
            return self.__stop_ord_handler.process(order, price, qty)
        return False

    def execute(self, order, filled_price, filled_qty):
        if order.is_done():
            return False

        if filled_qty < order.leave_qty():
            self.__send_exec_report(order, filled_price, filled_qty, OrdStatus.PARTIALLY_FILLED)
            return False
        else:
            filled_qty = order.leave_qty()
            self.__send_exec_report(order, filled_price, filled_qty, OrdStatus.FILLED)
            self.__remove_order(order)
            return True

    def __send_exec_report(self, order, filled_price, filled_qty, ord_status):
        exec_report = ExecutionReport(broker_id=Simulator.ID, ord_id=order.ord_id, instrument=order.instrument,
                                      timestamp=clock.current_date_time(), er_id=self.next_exec_id(),
                                      filled_qty=filled_qty,
                                      filled_price=filled_price, ord_status=ord_status)

        order_mgr.on_exec_report(exec_report)


broker_mapping = {
    Simulator.ID: Simulator()
}


def get_broker(broker_id):
    return broker_mapping[broker_id]
