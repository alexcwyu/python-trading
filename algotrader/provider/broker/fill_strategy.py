import abc

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.event.order import OrdType
from algotrader.provider.broker.order_handler import MarketOrderHandler, LimitOrderHandler, StopLimitOrderHandler, \
    StopOrderHandler, TrailingStopOrderHandler
from algotrader.provider.broker.sim_config import SimConfig
from algotrader.provider.broker.slippage import NoSlippage
from algotrader.trading import inst_data_mgr


class FillStrategy(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process_new_order(self, order):
        raise NotImplementedError()

    @abc.abstractmethod
    def process_w_market_data(self, market_data):
        raise NotImplementedError()

    @abc.abstractmethod
    def process_w_price_qty(self, order, price, qty):
        raise NotImplementedError()


class DefaultFillStrategy(FillStrategy):
    def __init__(self, sim_config=None, slippage = None):
        self.__sim_config = sim_config if sim_config else SimConfig()
        self.__slippage = slippage if slippage else NoSlippage()
        self.__market_ord_handler = MarketOrderHandler(self.__sim_config, self.__slippage)
        self.__limit_ord_handler = LimitOrderHandler(self.__sim_config)
        self.__stop_limit_ord_handler = StopLimitOrderHandler(self.__sim_config)
        self.__stop_ord_handler = StopOrderHandler(self.__sim_config, self.__slippage)
        self.__trailing_stop_ord_handler = TrailingStopOrderHandler(self.__sim_config, self.__slippage)

    def process_new_order(self, order):
        fill_info = None
        config = self.__sim_config

        quote = inst_data_mgr.get_quote(order.instrument)
        trade = inst_data_mgr.get_trade(order.instrument)
        bar = inst_data_mgr.get_bar(order.instrument)

        if not fill_info and config.fill_on_quote and config.fill_on_bar_mode == SimConfig.FillMode.LAST and quote:
            fill_info = self.process_w_market_data(order, quote, True)
        elif not fill_info and config.fill_on_trade and config.fill_on_trade_mode == SimConfig.FillMode.LAST and trade:
            fill_info = self.process_w_market_data(order, trade, True)
        elif not fill_info and config.fill_on_bar and config.fill_on_bar_mode == SimConfig.FillMode.LAST and bar:
            fill_info = self.process_w_market_data(order, bar, True)

        return fill_info

    def process_w_market_data(self, order, event, new_order=False):

        config = self.__sim_config

        if not event \
                or (isinstance(event, Bar) and not config.fill_on_bar) \
                or (isinstance(event, Trade) and not config.fill_on_trade) \
                or (isinstance(event, Quote) and not config.fill_on_quote):
            return None

        if order.type == OrdType.MARKET:
            return self.__market_ord_handler.process(order, event, new_order)
        elif order.type == OrdType.LIMIT:
            return self.__limit_ord_handler.process(order, event, new_order)
        elif order.type == OrdType.STOP_LIMIT:
            return self.__stop_limit_ord_handler.process(order, event, new_order)
        elif order.type == OrdType.STOP:
            return self.__stop_ord_handler.process(order, event, new_order)
        elif order.type == OrdType.TRAILING_STOP:
            return self.__trailing_stop_ord_handler.process(order, event, new_order)
        assert False

    def process_w_price_qty(self, order, price, qty):
        if order.type == OrdType.MARKET:
            return self.__market_ord_handler.process_w_price_qty(order, price, qty)
        elif order.type == OrdType.LIMIT:
            return self.__limit_ord_handler.process_w_price_qty(order, price, qty)
        elif order.type == OrdType.STOP_LIMIT:
            return self.__stop_limit_ord_handler.process_w_price_qty(order, price, qty)
        elif order.type == OrdType.STOP:
            return self.__stop_ord_handler.process_w_price_qty(order, price, qty)
        elif order.type == OrdType.TRAILING_STOP:
            return self.__trailing_stop_ord_handler.process_w_price_qty(order, price, qty)
        return None
