import abc
import sys

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.event.order import OrdAction
from algotrader.provider.broker.data_processor import BarProcessor, TradeProcessor, QuoteProcessor


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
        raise NotImplementedError()

    @abc.abstractmethod
    def process_w_trade(self, order, trade):
        raise NotImplementedError()

    @abc.abstractmethod
    def process_w_bar(self, order, bar):
        raise NotImplementedError()

    @abc.abstractmethod
    def process_w_price_qty(self, order, price, qty):
        raise NotImplementedError()


class MarketOrderHandler(SimOrderHandler):
    def __init__(self, execute_func = None, config = None):
        super(MarketOrderHandler, self).__init__(execute_func = None, config = None)

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
        raise NotImplementedError()

    @abc.abstractmethod
    def stop_limit_w_price_qty(self, order, price, qty):
        raise NotImplementedError()


class LimitOrderHandler(AbstractStopLimitOrderHandler):
    def __init__(self, execute_func, config):
        super(LimitOrderHandler, self).__init__(execute_func, config)

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
        super(StopLimitOrderHandler, self).__init__(execute_func, config)

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
        super(StopOrderHandler, self).__init__(execute_func, config)

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
        super(TrailingStopOrderHandler, self).__init__(execute_func, config)

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
