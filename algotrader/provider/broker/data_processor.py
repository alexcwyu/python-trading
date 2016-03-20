import abc

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.event.order import OrdAction
from algotrader.provider.broker.sim_config import SimConfig


class MarketDataProcessor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_price(self, order, market_data, config):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_qty(self, order, market_data, config):
        raise NotImplementedError()


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
