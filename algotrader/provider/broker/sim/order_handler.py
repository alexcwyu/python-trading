import abc
import sys
from collections import defaultdict

from algotrader.model.market_data_pb2 import Bar, Quote, Trade
from algotrader.provider.broker.sim.data_processor import BarProcessor, TradeProcessor, QuoteProcessor
from algotrader.utils.trade_data_utils import TradeDataUtils


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

    def process(self, new_ord_req, event, new_order=False):
        if event:
            if isinstance(event, Bar):
                fill_qty = self._bar_processor.get_qty(new_ord_req, event, self._config)
                return self.process_w_bar(new_ord_req, event, fill_qty, new_order)
            elif isinstance(event, Quote):
                fill_price = self._quote_processor.get_price(new_ord_req, event, self._config, new_order)
                fill_qty = self._quote_processor.get_qty(new_ord_req, event, self._config)
                if fill_price <= 0.0 or fill_qty <= 0:
                    return None
                return self.process_w_price_qty(new_ord_req, fill_price, fill_qty)
            elif isinstance(event, Trade):
                fill_price = self._trade_processor.get_price(new_ord_req, event, self._config, new_order)
                fill_qty = self._trade_processor.get_qty(new_ord_req, event, self._config)
                if fill_price <= 0.0 or fill_qty <= 0:
                    return None
                return self.process_w_price_qty(new_ord_req, fill_price, fill_qty)
        return None

    @abc.abstractmethod
    def process_w_bar(self, new_ord_req, bar, new_order=False):
        raise NotImplementedError()

    @abc.abstractmethod
    def process_w_price_qty(self, new_ord_req, price, qty):
        raise NotImplementedError()


class MarketOrderHandler(SimOrderHandler):
    def __init__(self, config, slippage=None):
        super(MarketOrderHandler, self).__init__(config)
        self.__slippage = slippage

    def process_w_bar(self, new_ord_req, bar, qty, new_order=False):
        fill_price = self._bar_processor.get_price(new_ord_req, bar, self._config, new_order)
        if fill_price <= 0.0 or qty <= 0:
            return None
        if self.__slippage:
            fill_price = self.__slippage.calc_price_w_bar(new_ord_req, fill_price, qty, bar)
        return FillInfo(qty, fill_price)

    def process_w_price_qty(self, new_ord_req, price, qty):
        return FillInfo(qty, price)


class LimitOrderHandler(SimOrderHandler):
    def __init__(self, config):
        super(LimitOrderHandler, self).__init__(config)

    def process_w_bar(self, new_ord_req, bar, qty, new_order=False):
        if TradeDataUtils.is_buy(new_ord_req) and bar.low <= new_ord_req.limit_price:
            return FillInfo(qty, new_ord_req.limit_price)
        elif TradeDataUtils.is_sell(new_ord_req) and bar.high >= new_ord_req.limit_price:
            return FillInfo(qty, new_ord_req.limit_price)
        return None

    def process_w_price_qty(self, new_ord_req, price, qty):
        if TradeDataUtils.is_buy(new_ord_req) and price <= new_ord_req.limit_price:
            return FillInfo(qty, new_ord_req.limit_price)
        elif TradeDataUtils.is_sell(new_ord_req) and price >= new_ord_req.limit_price:
            return FillInfo(qty, new_ord_req.limit_price)
        return None


class StopLimitOrderHandler(SimOrderHandler):
    def __init__(self, config):
        super(StopLimitOrderHandler, self).__init__(config)
        self.__stop_limit_ready = defaultdict(dict)

    def process_w_bar(self, new_ord_req, bar, qty, new_order=False):
        stop_limit_ready = self.__stop_limit_ready[new_ord_req.cl_id].get(new_ord_req.cl_ord_id, False)
        if TradeDataUtils.is_buy(new_ord_req):
            if not stop_limit_ready and bar.high >= new_ord_req.stop_price:
                self.__stop_limit_ready[new_ord_req.cl_id][new_ord_req.cl_ord_id] = True
            elif stop_limit_ready and bar.low <= new_ord_req.limit_price:
                return FillInfo(qty, new_ord_req.limit_price)
        elif TradeDataUtils.is_sell(new_ord_req):
            if not stop_limit_ready and bar.low <= new_ord_req.stop_price:
                self.__stop_limit_ready[new_ord_req.cl_id][new_ord_req.cl_ord_id] = True
            elif stop_limit_ready and bar.high >= new_ord_req.limit_price:
                return FillInfo(qty, new_ord_req.limit_price)
        return None

    def process_w_price_qty(self, new_ord_req, price, qty):
        stop_limit_ready = self.__stop_limit_ready[new_ord_req.cl_id].get(new_ord_req.cl_ord_id, False)
        if TradeDataUtils.is_buy(new_ord_req):
            if not stop_limit_ready and price >= new_ord_req.stop_price:
                self.__stop_limit_ready[new_ord_req.cl_id][new_ord_req.cl_ord_id] = True
            elif stop_limit_ready and price <= new_ord_req.limit_price:
                return FillInfo(qty, price)
        elif TradeDataUtils.is_sell(new_ord_req):
            if not stop_limit_ready and price <= new_ord_req.stop_price:
                self.__stop_limit_ready[new_ord_req.cl_id][new_ord_req.cl_ord_id] = True
            elif stop_limit_ready and price >= new_ord_req.limit_price:
                return FillInfo(qty, price)
        return None

    def stop_limit_ready(self, cl_id, cl_ord_id):
        return self.__stop_limit_ready[cl_id].get(cl_ord_id, False)


class StopOrderHandler(SimOrderHandler):
    def __init__(self, config, slippage=None):
        super(StopOrderHandler, self).__init__(config)
        self.__slippage = slippage
        self.__stop_limit_ready = defaultdict(dict)

    def process_w_bar(self, new_ord_req, bar, qty, new_order=False):
        stop_limit_ready = self.__stop_limit_ready[new_ord_req.cl_id].get(new_ord_req.cl_ord_id, False)
        if TradeDataUtils.is_buy(new_ord_req):
            if bar.high >= new_ord_req.stop_price:
                self.__stop_limit_ready[new_ord_req.cl_id][new_ord_req.cl_ord_id] = True
                fill_price = new_ord_req.stop_price
                if self.__slippage:
                    fill_price = self.__slippage.calc_price_w_bar(new_ord_req, fill_price, qty, bar)
                return FillInfo(qty, fill_price)
        elif TradeDataUtils.is_sell(new_ord_req):
            if bar.low <= new_ord_req.stop_price:
                self.__stop_limit_ready[new_ord_req.cl_id][new_ord_req.cl_ord_id] = True
                fill_price = new_ord_req.stop_price
                if self.__slippage:
                    fill_price = self.__slippage.calc_price_w_bar(new_ord_req, fill_price, qty, bar)
                return FillInfo(qty, fill_price)
        return None

    def process_w_price_qty(self, new_ord_req, price, qty):
        stop_limit_ready = self.__stop_limit_ready[new_ord_req.cl_id].get(new_ord_req.cl_ord_id, False)
        if TradeDataUtils.is_buy(new_ord_req):
            if price >= new_ord_req.stop_price:
                self.__stop_limit_ready[new_ord_req.cl_id][new_ord_req.cl_ord_id] = True
                return FillInfo(qty, price)
        elif TradeDataUtils.is_sell(new_ord_req):
            if price <= new_ord_req.stop_price:
                self.__stop_limit_ready[new_ord_req.cl_id][new_ord_req.cl_ord_id] = True
                return FillInfo(qty, price)
        return None

    def stop_limit_ready(self, cl_id, cl_ord_id):
        return self.__stop_limit_ready[cl_id].get(cl_ord_id, False)


class TrailingStopOrderHandler(SimOrderHandler):
    def __init__(self, config, slippage=None):
        super(TrailingStopOrderHandler, self).__init__(config)
        self.__slippage = slippage
        self.__trailing_stop_exec_price = defaultdict(dict)

    def _init_order_trailing_stop(self, new_ord_req):
        trailing_stop_exec_price = self.__trailing_stop_exec_price[new_ord_req.cl_id].get(new_ord_req.cl_ord_id, 0)
        if trailing_stop_exec_price == 0:
            if TradeDataUtils.is_buy(new_ord_req):
                self.__trailing_stop_exec_price[new_ord_req.cl_id][new_ord_req.cl_ord_id] = sys.float_info.max
            elif TradeDataUtils.is_sell(new_ord_req):
                self.__trailing_stop_exec_price[new_ord_req.cl_id][new_ord_req.cl_ord_id] = sys.float_info.min

    def process_w_bar(self, new_ord_req, bar, qty, new_order=False):
        self._init_order_trailing_stop(new_ord_req)
        trailing_stop_exec_price = self.__trailing_stop_exec_price[new_ord_req.cl_id][new_ord_req.cl_ord_id]
        if TradeDataUtils.is_buy(new_ord_req):
            trailing_stop_exec_price = min(trailing_stop_exec_price, bar.low + new_ord_req.stop_price)
            self.__trailing_stop_exec_price[new_ord_req.cl_id][new_ord_req.cl_ord_id] = trailing_stop_exec_price
            if bar.high >= trailing_stop_exec_price:
                fill_price = trailing_stop_exec_price
                if self.__slippage:
                    fill_price = self.__slippage.calc_price_w_bar(new_ord_req, fill_price, qty, bar)
                return FillInfo(qty, fill_price)
        elif TradeDataUtils.is_sell(new_ord_req):
            trailing_stop_exec_price = max(trailing_stop_exec_price, bar.high - new_ord_req.stop_price)
            self.__trailing_stop_exec_price[new_ord_req.cl_id][new_ord_req.cl_ord_id] = trailing_stop_exec_price

            if bar.low <= trailing_stop_exec_price:
                fill_price = trailing_stop_exec_price
                if self.__slippage:
                    fill_price = self.__slippage.calc_price_w_bar(new_ord_req, fill_price, qty, bar)
                return FillInfo(qty, fill_price)
        return None

    def process_w_price_qty(self, new_ord_req, price, qty):
        self._init_order_trailing_stop(new_ord_req)
        trailing_stop_exec_price = self.__trailing_stop_exec_price[new_ord_req.cl_id][new_ord_req.cl_ord_id]
        if TradeDataUtils.is_buy(new_ord_req):
            trailing_stop_exec_price = min(trailing_stop_exec_price, price + new_ord_req.stop_price)
            self.__trailing_stop_exec_price[new_ord_req.cl_id][new_ord_req.cl_ord_id] = trailing_stop_exec_price
            if price >= trailing_stop_exec_price:
                return FillInfo(qty, trailing_stop_exec_price)
        elif TradeDataUtils.is_sell(new_ord_req):
            trailing_stop_exec_price = max(trailing_stop_exec_price, price - new_ord_req.stop_price)
            self.__trailing_stop_exec_price[new_ord_req.cl_id][new_ord_req.cl_ord_id] = trailing_stop_exec_price
            if price <= trailing_stop_exec_price:
                return FillInfo(qty, trailing_stop_exec_price)
        return None

    def trailing_stop_exec_price(self, cl_id, cl_ord_id):
        return self.__trailing_stop_exec_price[cl_id].get(cl_ord_id, 0)
