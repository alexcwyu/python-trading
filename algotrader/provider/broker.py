import abc
import sys

from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import Bar, Trade, Quote
from algotrader.event.order import MarketDataEventHandler, OrderEventHandler, OrdType, OrdStatus, ExecutionReport, \
    OrdAction, OrderStatusUpdate
from algotrader.provider import Provider
from algotrader.tools import *
from algotrader.trading.clock import default_clock
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.trading.order_mgr import order_mgr
from algotrader.provider.broker_mgr import broker_mgr
from collections import defaultdict

# from algotrader.tools import *


class Broker(Provider, OrderEventHandler):
    __metaclass__ = abc.ABCMeta

    def start(self):
        pass


class MarketDataProcessor:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_price(self, order, market_data, config):
        pass

    @abc.abstractmethod
    def get_qty(self, order, market_data, config):
        pass


class BarProcessor(MarketDataProcessor):
    def get_price(self, order, market_data, config):
        if market_data and isinstance(market_data, Bar):
            if config.fill_on_bar_mode == SimConfig.FillMode.LAST or config.fill_on_bar_mode == SimConfig.FillMode.NEXT_CLOSE:
                return market_data.close_or_adj_close()
            elif config.fill_on_bar_mode == SimConfig.FillMode.NEXT_OPEN:
                return market_data.open
        return 0.0

    def get_qty(self, order, market_data, config):
        return order.qty


class QuoteProcessor(MarketDataProcessor):
    def get_price(self, order, market_data, config):
        if market_data and isinstance(market_data, Quote):
            if order.action == OrdAction.BUY and market_data.ask > 0:
                return market_data.ask
            elif order.action == OrdAction.SELL and market_data.bid > 0:
                return market_data.bid
        return 0.0

    def get_qty(self, order, market_data, config):
        if market_data and isinstance(market_data, Quote) and config.partial_fill:
            if order.action == OrdAction.BUY and market_data.ask_size > 0:
                return market_data.ask_size
            elif order.action == OrdAction.SELL and market_data.bid_size > 0:
                return market_data.bid_size
        return order.qty


class TradeProcessor(MarketDataProcessor):
    def get_price(self, order, market_data, config):
        if market_data and isinstance(market_data, Trade):
            if market_data.price > 0:
                return market_data.price
        return 0.0

    def get_qty(self, order, market_data, config):
        return order.qty


class SimOrderHandler(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, execute_func, config):
        self.execute_func = execute_func
        self._config = config
        self._bar_processor = BarProcessor()
        self._trade_processor = TradeProcessor()
        self._quote_processor = QuoteProcessor()

    def process(self, order, event):
        if isinstance(event, Bar):
            return self.process_w_bar(order, event)
        elif isinstance(event, Quote):
            return self.process_w_quote(order, event)
        elif isinstance(event, Trade):
            return self.process_w_trade(order, event)

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
    def __init__(self, execute_func, config):
        super(self.__class__, self).__init__(execute_func, config)

    def process_w_bar(self, order, bar):
        if bar:
            filled_price = self._bar_processor.get_price(order, bar, self._config)
            filled_qty = self._bar_processor.get_qty(order, bar, self._config)
            return self.process_w_price_qty(order, filled_price, filled_qty)
        return False

    def process_w_trade(self, order, trade):
        if trade:
            filled_price = self._trade_processor.get_price(order, trade, self._config)
            filled_qty = self._trade_processor.get_qty(order, trade, self._config)
            return self.process_w_price_qty(order, filled_price, filled_qty)
        return False

    def process_w_quote(self, order, quote):
        if quote:
            filled_price = self._quote_processor.get_price(order, quote, self._config)
            filled_qty = self._quote_processor.get_qty(order, quote, self._config)
            return self.process_w_price_qty(order, filled_price, filled_qty)
        return False

    def process_w_price_qty(self, order, price, qty):
        return self.execute_func(order, price, qty)


class AbstractStopLimitOrderHandler(SimOrderHandler):
    __metaclass__ = abc.ABCMeta

    def __init__(self, execute_func, config):
        super(AbstractStopLimitOrderHandler, self).__init__(execute_func, config)

    def process_w_bar(self, order, bar):
        if bar:
            filled_qty = self._bar_processor.get_qty(order, bar, self._config)
            return self.stop_limit_w_bar(order, bar, filled_qty)
        return False

    def process_w_trade(self, order, trade):
        if trade:
            filled_price = self._trade_processor.get_price(order, trade, self._config)
            filled_qty = self._trade_processor.get_qty(order, trade, self._config)
            return self.process_w_price_qty(order, filled_price, filled_qty)
        return False

    def process_w_quote(self, order, quote):
        if quote:
            filled_price = self._quote_processor.get_price(order, quote, self._config)
            filled_qty = self._quote_processor.get_qty(order, quote, self._config)
            return self.process_w_price_qty(order, filled_price, filled_qty)
        return False

    def process_w_price_qty(self, order, price, qty):
        return self.stop_limit_w_price_qty(order, price, qty)

    @abc.abstractmethod
    def stop_limit_w_bar(self, order, bar, qty):
        pass

    @abc.abstractmethod
    def stop_limit_w_price_qty(self, order, price, qty):
        pass


class LimitOrderHandler(AbstractStopLimitOrderHandler):
    def __init__(self, execute_func, config):
        super(self.__class__, self).__init__(execute_func, config)

    def stop_limit_w_bar(self, order, bar, qty):
        if order.action == OrdAction.BUY and bar.low <= order.limit_price:
            return self.execute_func(order, order.limit_price, qty)
        elif order.action == OrdAction.SELL and bar.high >= order.limit_price:
            return self.execute_func(order, order.limit_price, qty)
        return False

    def stop_limit_w_price_qty(self, order, price, qty):
        if order.action == OrdAction.BUY and price <= order.limit_price:
            return self.execute_func(order, order.limit_price, qty)
        elif order.action == OrdAction.SELL and price >= order.limit_price:
            return self.execute_func(order, order.limit_price, qty)
        return False


class StopLimitOrderHandler(AbstractStopLimitOrderHandler):
    def __init__(self, execute_func, config):
        super(self.__class__, self).__init__(execute_func, config)

    def stop_limit_w_bar(self, order, bar, qty):
        if order.action == OrdAction.BUY:
            if not order.stop_limit_ready and bar.high >= order.stop_price:
                order.stop_limit_ready = True
            elif order.stop_limit_ready and bar.low <= order.limit_price:
                return self.execute_func(order, order.limit_price, qty)
        elif order.action == OrdAction.SELL:
            if not order.stop_limit_ready and bar.low <= order.stop_price:
                order.stop_limit_ready = True
            elif order.stop_limit_ready and bar.high >= order.limit_price:
                return self.execute_func(order, order.limit_price, qty)
        return False

    def stop_limit_w_price_qty(self, order, price, qty):
        if order.action == OrdAction.BUY:
            if not order.stop_limit_ready and price >= order.stop_price:
                order.stop_limit_ready = True
            elif order.stop_limit_ready and price <= order.limit_price:
                return self.execute_func(order, price, qty)
        elif order.action == OrdAction.SELL:
            if not order.stop_limit_ready and price <= order.stop_price:
                order.stop_limit_ready = True
            elif order.stop_limit_ready and price >= order.limit_price:
                return self.execute_func(order, price, qty)
        return False


class StopOrderHandler(AbstractStopLimitOrderHandler):
    def __init__(self, execute_func, config):
        super(self.__class__, self).__init__(execute_func, config)

    def stop_limit_w_bar(self, order, bar, qty):
        if order.action == OrdAction.BUY:
            if bar.high >= order.stop_price:
                order.stop_limit_ready = True
                return self.execute_func(order, order.stop_price, qty)
        elif order.action == OrdAction.SELL:
            if bar.low <= order.stop_price:
                order.stop_limit_ready = True
                return self.execute_func(order, order.stop_price, qty)
        return False

    def stop_limit_w_price_qty(self, order, price, qty):
        if order.action == OrdAction.BUY:
            if price >= order.stop_price:
                order.stop_limit_ready = True
                return self.execute_func(order, price, qty)
        elif order.action == OrdAction.SELL:
            if price <= order.stop_price:
                order.stop_limit_ready = True
                return self.execute_func(order, price, qty)
        return False


class TrailingStopOrderHandler(AbstractStopLimitOrderHandler):
    def __init__(self, execute_func, config):
        super(self.__class__, self).__init__(execute_func, config)

    def _init_order_trailing_stop(self, order):
        if order.trailing_stop_exec_price == 0:
            if order.action == OrdAction.BUY:
                order.trailing_stop_exec_price = sys.float_info.max
            elif order.action == OrdAction.SELL:
                order.trailing_stop_exec_price = sys.float_info.min

    def stop_limit_w_bar(self, order, bar, qty):
        self._init_order_trailing_stop(order)
        if order.action == OrdAction.BUY:
            order.trailing_stop_exec_price = min(order.trailing_stop_exec_price, bar.low + order.stop_price)

            if (bar.high >= order.trailing_stop_exec_price):
                return self.execute_func(order, order.trailing_stop_exec_price, qty)
        elif order.action == OrdAction.SELL:
            order.trailing_stop_exec_price = max(order.trailing_stop_exec_price, bar.high - order.stop_price)

            if (bar.low <= order.trailing_stop_exec_price):
                return self.execute_func(order, order.trailing_stop_exec_price, qty)
        return False

    def stop_limit_w_price_qty(self, order, price, qty):
        self._init_order_trailing_stop(order)
        if order.action == OrdAction.BUY:
            order.trailing_stop_exec_price = min(order.trailing_stop_exec_price, price + order.stop_price)

            if (price >= order.trailing_stop_exec_price):
                return self.execute_func(order, order.trailing_stop_exec_price, qty)
        elif order.action == OrdAction.SELL:
            order.trailing_stop_exec_price = max(order.trailing_stop_exec_price, price - order.stop_price)

            if (price <= order.trailing_stop_exec_price):
                return self.execute_func(order, order.trailing_stop_exec_price, qty)
        return False


class SimConfig:
    class FillMode:
        LAST = 0
        NEXT_OPEN = 1
        NEXT_CLOSE = 2

    def __init__(self, partial_fill=True,
                 fill_on_quote=True,
                 fill_on_trade=True,
                 fill_on_bar=True,
                 fill_on_quote_mode=FillMode.LAST,
                 fill_on_trade_mode=FillMode.LAST,
                 fill_on_bar_mode=FillMode.LAST):
        self.partial_fill = partial_fill
        self.fill_on_quote = fill_on_quote
        self.fill_on_trade = fill_on_trade
        self.fill_on_bar = fill_on_bar
        self.fill_on_quote_mode = fill_on_quote_mode
        self.fill_on_trade_mode = fill_on_trade_mode
        self.fill_on_bar_mode = fill_on_bar_mode


#@singleton
class Simulator(Broker, MarketDataEventHandler):
    ID = "Simulator"

    def __init__(self, sim_config=None, exec_handler=order_mgr):
        self.__next_exec_id = 0
        self.__order_map = defaultdict(dict)
        self.__quote_map = {}
        self.__sim_config = sim_config if sim_config else SimConfig()
        self.__exec__handler = exec_handler
        self.__market_ord_handler = MarketOrderHandler(self.execute, self.__sim_config)
        self.__limit_ord_handler = LimitOrderHandler(self.execute, self.__sim_config)
        self.__stop_limit_ord_handler = StopLimitOrderHandler(self.execute, self.__sim_config)
        self.__stop_ord_handler = StopOrderHandler(self.execute, self.__sim_config)
        self.__trailing_stop_ord_handler = TrailingStopOrderHandler(self.execute, self.__sim_config)
        broker_mgr.reg_broker(self)

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def stop(self):
        pass

    def id(self):
        return Simulator.ID

    def next_exec_id(self):
        __next_exec_id = self.__next_exec_id
        self.__next_exec_id += 1
        return __next_exec_id

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        if self.__sim_config.fill_on_bar and bar.instrument in self.__order_map:
            for order in self.__order_map[bar.instrument].values():
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
        orders = self.__order_map[order.instrument]
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
            # TODO fix it, we should handle the fill sequentially, from quote, then trade, then bar
            if not executed and config.fill_on_quote and config.fill_on_bar_mode == SimConfig.FillMode.LAST and quote:
                executed = self.__market_ord_handler.process_w_quote(order, quote)
            elif not executed and config.fill_on_trade and config.fill_on_trade_mode == SimConfig.FillMode.LAST and trade:
                executed = self.__market_ord_handler.process_w_trade(order, trade)
            elif not executed and config.fill_on_bar and config.fill_on_bar_mode == SimConfig.FillMode.LAST and bar:
                executed = self.__market_ord_handler.process_w_bar(order, bar)
        else:
            # TODO fix it, we should handle the fill sequentially, from quote, then trade, then bar
            if not executed and config.fill_on_quote and quote:
                executed = self.__process(order, quote)
            elif not executed and config.fill_on_trade and trade:
                executed = self.__process(order, trade)
            elif not executed and config.fill_on_bar and bar:
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
        elif order.type == OrdType.TRAILING_STOP:
            return self.__trailing_stop_ord_handler.process(order, event)
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
        elif order.type == OrdType.TRAILING_STOP:
            return self.__trailing_stop_ord_handler.process(order, price, qty)
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

    def __send_status(self, order, ord_status):
        ord_update = OrderStatusUpdate(broker_id=Simulator.ID, ord_id=order.ord_id, instrument=order.instrument,
                                   timestamp=default_clock.current_date_time(), status = ord_status)
        self.__exec__handler.on_ord_upd(ord_update)

    def __send_exec_report(self, order, filled_price, filled_qty, ord_status):
        exec_report = ExecutionReport(broker_id=Simulator.ID, ord_id=order.ord_id, instrument=order.instrument,
                                      timestamp=default_clock.current_date_time(), er_id=self.next_exec_id(),
                                      filled_qty=filled_qty,
                                      filled_price=filled_price, status=ord_status)

        self.__exec__handler.on_exec_report(exec_report)

    def _get_orders(self):
        return self.__order_map


# broker_mapping = {
#     Simulator.ID: Simulator()
# }
#
#
# def get_broker(broker_id):
#     return broker_mapping[broker_id]

simulator = Simulator();