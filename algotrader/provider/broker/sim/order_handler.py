import abc
import sys

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.provider.broker.sim.data_processor import BarProcessor, TradeProcessor, QuoteProcessor


class FillInfo(object):
    def __init__(self, fill_qty, fill_price):
        self.fill_qty = fill_qty
        self.fill_price = fill_price


class SimOrderHandler(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        self._config = config
        self._bar_processor = BarProcessor()
        self._trade_processor = TradeProcessor()
        self._quote_processor = QuoteProcessor()

    def process(self, order, event, new_order = False):
        if event:
            if isinstance(event, Bar):
                fill_qty = self._bar_processor.get_qty(order, event, self._config)
                return self.process_w_bar(order, event, fill_qty, new_order)
            elif isinstance(event, Quote):
                fill_price = self._quote_processor.get_price(order, event, self._config, new_order)
                fill_qty = self._quote_processor.get_qty(order, event, self._config)
                if fill_price <= 0.0 or fill_qty <=0:
                    return None
                return self.process_w_price_qty(order, fill_price, fill_qty)
            elif isinstance(event, Trade):
                fill_price = self._trade_processor.get_price(order, event, self._config, new_order)
                fill_qty = self._trade_processor.get_qty(order, event, self._config)
                if fill_price <= 0.0 or fill_qty <=0:
                    return None
                return self.process_w_price_qty(order, fill_price, fill_qty)
        return None

    @abc.abstractmethod
    def process_w_bar(self, order, bar, new_order=False):
        raise NotImplementedError()

    @abc.abstractmethod
    def process_w_price_qty(self, order, price, qty):
        raise NotImplementedError()


class MarketOrderHandler(SimOrderHandler):
    def __init__(self, config, slippage = None):
        super(MarketOrderHandler, self).__init__(config)
        self.__slippage = slippage

    def process_w_bar(self, order, bar, qty, new_order=False):
        fill_price = self._bar_processor.get_price(order, bar, self._config, new_order)
        if fill_price <= 0.0 or qty <=0:
            return None
        if self.__slippage:
            fill_price = self.__slippage.calc_price_w_bar(order, fill_price, qty, bar)
        return FillInfo(qty, fill_price)

    def process_w_price_qty(self, order, price, qty):
        return FillInfo(qty, price)


class LimitOrderHandler(SimOrderHandler):
    def __init__(self, config):
        super(LimitOrderHandler, self).__init__(config)

    def process_w_bar(self, order, bar, qty, new_order=False):
        if order.is_buy() and bar.low <= order.limit_price:
            return FillInfo(qty, order.limit_price)
        elif order.is_sell() and bar.high >= order.limit_price:
            return FillInfo(qty, order.limit_price)
        return None

    def process_w_price_qty(self, order, price, qty):
        if order.is_buy() and price <= order.limit_price:
            return FillInfo(qty, order.limit_price)
        elif order.is_sell() and price >= order.limit_price:
            return FillInfo(qty, order.limit_price)
        return None


class StopLimitOrderHandler(SimOrderHandler):
    def __init__(self, config):
        super(StopLimitOrderHandler, self).__init__(config)

    def process_w_bar(self, order, bar, qty, new_order=False):
        if order.is_buy():
            if not order.stop_limit_ready and bar.high >= order.stop_price:
                order.stop_limit_ready = True
            elif order.stop_limit_ready and bar.low <= order.limit_price:
                return FillInfo(qty, order.limit_price)
        elif order.is_sell():
            if not order.stop_limit_ready and bar.low <= order.stop_price:
                order.stop_limit_ready = True
            elif order.stop_limit_ready and bar.high >= order.limit_price:
                return FillInfo(qty, order.limit_price)
        return None

    def process_w_price_qty(self, order, price, qty):
        if order.is_buy():
            if not order.stop_limit_ready and price >= order.stop_price:
                order.stop_limit_ready = True
            elif order.stop_limit_ready and price <= order.limit_price:
                return FillInfo(qty, price)
        elif order.is_sell():
            if not order.stop_limit_ready and price <= order.stop_price:
                order.stop_limit_ready = True
            elif order.stop_limit_ready and price >= order.limit_price:
                return FillInfo(qty, price)
        return None


class StopOrderHandler(SimOrderHandler):
    def __init__(self, config, slippage = None):
        super(StopOrderHandler, self).__init__(config)
        self.__slippage = slippage

    def process_w_bar(self, order, bar, qty, new_order=False):
        if order.is_buy():
            if bar.high >= order.stop_price:
                order.stop_limit_ready = True
                fill_price = order.stop_price
                if self.__slippage:
                    fill_price = self.__slippage.calc_price_w_bar(order, fill_price, qty, bar)
                return FillInfo(qty, fill_price)
        elif order.is_sell():
            if bar.low <= order.stop_price:
                order.stop_limit_ready = True
                fill_price = order.stop_price
                if self.__slippage:
                    fill_price = self.__slippage.calc_price_w_bar(order, fill_price, qty, bar)
                return FillInfo(qty, fill_price)
        return None

    def process_w_price_qty(self, order, price, qty):
        if order.is_buy():
            if price >= order.stop_price:
                order.stop_limit_ready = True
                return FillInfo(qty, price)
        elif order.is_sell():
            if price <= order.stop_price:
                order.stop_limit_ready = True
                return FillInfo(qty, price)
        return None


class TrailingStopOrderHandler(SimOrderHandler):
    def __init__(self, config, slippage = None):
        super(TrailingStopOrderHandler, self).__init__(config)
        self.__slippage = slippage

    def _init_order_trailing_stop(self, order):
        if order.trailing_stop_exec_price == 0:
            if order.is_buy():
                order.trailing_stop_exec_price = sys.float_info.max
            elif order.is_sell():
                order.trailing_stop_exec_price = sys.float_info.min

    def process_w_bar(self, order, bar, qty, new_order=False):
        self._init_order_trailing_stop(order)
        if order.is_buy():
            order.trailing_stop_exec_price = min(order.trailing_stop_exec_price, bar.low + order.stop_price)

            if bar.high >= order.trailing_stop_exec_price:
                fill_price = order.trailing_stop_exec_price
                if self.__slippage:
                    fill_price = self.__slippage.calc_price_w_bar(order, fill_price, qty, bar)
                return FillInfo(qty, fill_price)
        elif order.is_sell():
            order.trailing_stop_exec_price = max(order.trailing_stop_exec_price, bar.high - order.stop_price)

            if bar.low <= order.trailing_stop_exec_price:
                fill_price = order.trailing_stop_exec_price
                if self.__slippage:
                    fill_price = self.__slippage.calc_price_w_bar(order, fill_price, qty, bar)
                return FillInfo(qty, fill_price)
        return None

    def process_w_price_qty(self, order, price, qty):
        self._init_order_trailing_stop(order)
        if order.is_buy():
            order.trailing_stop_exec_price = min(order.trailing_stop_exec_price, price + order.stop_price)
            if price >= order.trailing_stop_exec_price:
                return FillInfo(qty, order.trailing_stop_exec_price)
        elif order.is_sell():
            order.trailing_stop_exec_price = max(order.trailing_stop_exec_price, price - order.stop_price)
            if price <= order.trailing_stop_exec_price:
                return FillInfo(qty, order.trailing_stop_exec_price)
        return None
