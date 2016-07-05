import abc
import math

from algotrader.event.market_data import Trade
from algotrader.provider.broker.sim.sim_config import SimConfig


class MarketDataProcessor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_price(self, new_ord_req, market_data, config, new_order=False):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_qty(self, new_ord_req, market_data, config):
        raise NotImplementedError()


class BarProcessor(MarketDataProcessor):
    def get_price(self, new_ord_req, market_data, config, new_order=False):
        if config.fill_on_bar_mode == SimConfig.FillMode.LAST or config.fill_on_bar_mode == SimConfig.FillMode.NEXT_CLOSE:
            return market_data.close
        elif not new_order and config.fill_on_bar_mode == SimConfig.FillMode.NEXT_OPEN:
            return market_data.open
        return 0.0

    def get_qty(self, new_ord_req, market_data, config):
        if config.partial_fill:
            bar_vol = math.trunc(
                market_data.vol if not config.bar_vol_ratio else market_data.vol * config.bar_vol_ratio)
            return min(new_ord_req.qty, bar_vol)
        return new_ord_req.qty


class QuoteProcessor(MarketDataProcessor):
    def get_price(self, new_ord_req, market_data, config, new_order=False):
        if new_ord_req.is_buy() and market_data.ask > 0:
            return market_data.ask
        elif new_ord_req.is_sell() and market_data.bid > 0:
            return market_data.bid
        return 0.0

    def get_qty(self, new_ord_req, market_data, config):
        if config.partial_fill:
            if new_ord_req.is_buy():
                return min(market_data.ask_size, new_ord_req.qty)
            elif new_ord_req.is_sell():
                return min(market_data.bid_size, new_ord_req.qty)
        return new_ord_req.qty


class TradeProcessor(MarketDataProcessor):
    def get_price(self, new_ord_req, market_data, config, new_order=False):
        if market_data and isinstance(market_data, Trade):
            if market_data.price > 0:
                return market_data.price
        return 0.0

    def get_qty(self, new_ord_req, market_data, config):
        if config.partial_fill:
            return min(new_ord_req.qty, market_data.size)
        return new_ord_req.qty
