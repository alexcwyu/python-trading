from collections import defaultdict

import numpy as np

from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.utils import logger
from algotrader.utils.time_series import DataSeries


class InstrumentDataManager(MarketDataEventHandler):
    def __init__(self):
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}

        self.__series_dict = {}

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__bar_dict[bar.instrument] = bar

        self.get_series(bar.id()).add(
            {"timestamp": bar.timestamp, "open": bar.open, "high": bar.high, "low": bar.low, "close": bar.close,
             "vol": bar.vol})

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__quote_dict[quote.instrument] = quote

        self.get_series(quote.id()).add(
            {"timestamp": quote.timestamp, "bid": quote.bid, "ask": quote.ask, "bid_size": quote.bid_size,
             "ask_size": quote.ask_size})

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__trade_dict[trade.instrument] = trade
        self.get_series(trade.id()).add({"timestamp": trade.timestamp, "price": trade.price, "size": trade.size})

    def get_bar(self, instrument):
        if instrument in self.__bar_dict:
            return self.__bar_dict[instrument]
        return None

    def get_quote(self, instrument):
        if instrument in self.__quote_dict:
            return self.__quote_dict[instrument]
        return None

    def get_trade(self, instrument):
        if instrument in self.__trade_dict:
            return self.__trade_dict[instrument]
        return None

    def get_latest_price(self, instrument):
        if instrument in self.__trade_dict:
            return self.__trade_dict[instrument].price
        elif instrument in self.__quote_dict:
            return self.__quote_dict[instrument].mid()
        elif instrument in self.__bar_dict:
            return self.__bar_dict[instrument].close
        return None

    def get_series(self, key, create_if_missing=True, cls=DataSeries, description=None, missing_value=np.nan):
        if type(key) == str:
            if key not in self.__series_dict:
                self.__series_dict[key] = cls(name=key, description=description, missing_value=missing_value)
            return self.__series_dict[key]
        raise AssertionError()

    def add_series(self, series, raise_if_duplicate=True):
        if series.name not in self.__series_dict:
            self.__series_dict[series.name] = series
        elif raise_if_duplicate and self.__series_dict[series.name] != series:
            raise AssertionError("Series [%s] already exist" % series.name)

    def has_series(self, name):
        return name in self.__series_dict

    def clear(self):
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}
        self.__series_dict = defaultdict(DataSeries)


inst_data_mgr = InstrumentDataManager()
