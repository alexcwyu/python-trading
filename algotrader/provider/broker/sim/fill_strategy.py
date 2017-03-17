import abc

from algotrader.model.market_data_pb2 import Bar, Quote, Trade
from algotrader.model.trade_data_pb2 import *
from algotrader.provider.broker.sim.order_handler import MarketOrderHandler, LimitOrderHandler, StopLimitOrderHandler, \
    StopOrderHandler, TrailingStopOrderHandler
from algotrader.provider.broker.sim.sim_config import SimConfig
from algotrader.provider.broker.sim.slippage import NoSlippage


class FillStrategy(object):
    Default = 0

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process_new_order(self, new_ord_req):
        raise NotImplementedError()

    @abc.abstractmethod
    def process_w_market_data(self, market_data):
        raise NotImplementedError()

    @abc.abstractmethod
    def process_w_price_qty(self, new_ord_req, price, qty):
        raise NotImplementedError()


class DefaultFillStrategy(FillStrategy):
    def __init__(self, app_context=None, sim_config=None, slippage=None):
        self.app_context = app_context
        self.__sim_config = sim_config if sim_config else SimConfig()
        self.__slippage = slippage if slippage else NoSlippage()
        self.__market_ord_handler = MarketOrderHandler(self.__sim_config, self.__slippage)
        self.__limit_ord_handler = LimitOrderHandler(self.__sim_config)
        self.__stop_limit_ord_handler = StopLimitOrderHandler(self.__sim_config)
        self.__stop_ord_handler = StopOrderHandler(self.__sim_config, self.__slippage)
        self.__trailing_stop_ord_handler = TrailingStopOrderHandler(self.__sim_config, self.__slippage)

    def process_new_order(self, new_ord_req):
        fill_info = None
        config = self.__sim_config

        quote = self.app_context.inst_data_mgr.get_quote(new_ord_req.inst_id)
        trade = self.app_context.inst_data_mgr.get_trade(new_ord_req.inst_id)
        bar = self.app_context.inst_data_mgr.get_bar(new_ord_req.inst_id)

        if not fill_info and config.fill_on_quote and config.fill_on_bar_mode == SimConfig.FillMode.LAST and quote:
            fill_info = self.process_w_market_data(new_ord_req, quote, True)
        elif not fill_info and config.fill_on_trade and config.fill_on_trade_mode == SimConfig.FillMode.LAST and trade:
            fill_info = self.process_w_market_data(new_ord_req, trade, True)
        elif not fill_info and config.fill_on_bar and config.fill_on_bar_mode == SimConfig.FillMode.LAST and bar:
            fill_info = self.process_w_market_data(new_ord_req, bar, True)

        return fill_info

    def process_w_market_data(self, new_ord_req, event, new_order=False):

        config = self.__sim_config

        if not event \
                or (isinstance(event, Bar) and not config.fill_on_bar) \
                or (isinstance(event, Trade) and not config.fill_on_trade) \
                or (isinstance(event, Quote) and not config.fill_on_quote):
            return None

        if new_ord_req.type == OrderType.MARKET:
            return self.__market_ord_handler.process(new_ord_req, event, new_order)
        elif new_ord_req.type == OrderType.LIMIT:
            return self.__limit_ord_handler.process(new_ord_req, event, new_order)
        elif new_ord_req.type == OrderType.STOP_LIMIT:
            return self.__stop_limit_ord_handler.process(new_ord_req, event, new_order)
        elif new_ord_req.type == OrderType.STOP:
            return self.__stop_ord_handler.process(new_ord_req, event, new_order)
        elif new_ord_req.type == OrderType.TRAILING_STOP:
            return self.__trailing_stop_ord_handler.process(new_ord_req, event, new_order)
        assert False

    def process_w_price_qty(self, new_ord_req, price, qty):
        if new_ord_req.type == OrderType.MARKET:
            return self.__market_ord_handler.process_w_price_qty(new_ord_req, price, qty)
        elif new_ord_req.type == OrderType.LIMIT:
            return self.__limit_ord_handler.process_w_price_qty(new_ord_req, price, qty)
        elif new_ord_req.type == OrderType.STOP_LIMIT:
            return self.__stop_limit_ord_handler.process_w_price_qty(new_ord_req, price, qty)
        elif new_ord_req.type == OrderType.STOP:
            return self.__stop_ord_handler.process_w_price_qty(new_ord_req, price, qty)
        elif new_ord_req.type == OrderType.TRAILING_STOP:
            return self.__trailing_stop_ord_handler.process_w_price_qty(new_ord_req, price, qty)
        return None
