import abc
import math

from algotrader.event.market_data import Trade
from algotrader.provider.broker.sim.sim_config import SimConfig


class MarketDataProcessor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_price(self, order, market_data, config, new_order=False):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_qty(self, order, market_data, config):
        raise NotImplementedError()


class BarProcessor(MarketDataProcessor):
    def get_price(self, order, market_data, config, new_order=False):
        if config.fill_on_bar_mode == SimConfig.FillMode.LAST or config.fill_on_bar_mode == SimConfig.FillMode.NEXT_CLOSE:
            return market_data.close
        elif not new_order and config.fill_on_bar_mode == SimConfig.FillMode.NEXT_OPEN:
            return market_data.open
        return 0.0

    def get_qty(self, order, market_data, config):
        if config.partial_fill:
            bar_vol = math.trunc(
                market_data.vol if not config.bar_vol_ratio else market_data.vol * config.bar_vol_ratio)
            return min(order.qty, bar_vol)
        return order.qty


class QuoteProcessor(MarketDataProcessor):
    def get_price(self, order, market_data, config, new_order=False):
        if order.is_buy() and market_data.ask > 0:
            return market_data.ask
        elif order.is_sell() and market_data.bid > 0:
            return market_data.bid
        return 0.0

    def get_qty(self, order, market_data, config):
        if config.partial_fill:
            if order.is_buy():
                return min(market_data.ask_size, order.qty)
            elif order.is_sell():
                return min(market_data.bid_size, order.qty)
        return order.qty


class TradeProcessor(MarketDataProcessor):
    def get_price(self, order, market_data, config, new_order=False):
        if market_data and isinstance(market_data, Trade):
            if market_data.price > 0:
                return market_data.price
        return 0.0

    def get_qty(self, order, market_data, config):
        if config.partial_fill:
            return min(order.qty, market_data.size)
        return order.qty
