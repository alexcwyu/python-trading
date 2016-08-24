from collections import defaultdict

import numpy as np

from algotrader.event.event_bus import EventBus
from algotrader.event.event_handler import MarketDataEventHandler
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
        self.__bar_dict[bar.inst_id] = bar

        self.get_series(bar.id()).add(
            {"timestamp": bar.timestamp, "inst_id": bar.inst_id, "open": bar.open, "high": bar.high, "low": bar.low, "close": bar.close,
             "vol": bar.vol})

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__quote_dict[quote.inst_id] = quote

        self.get_series(quote.id()).add(
            {"timestamp": quote.timestamp, "inst_id": quote.inst_id, "bid": quote.bid, "ask": quote.ask, "bid_size": quote.bid_size,
             "ask_size": quote.ask_size})

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__trade_dict[trade.inst_id] = trade
        self.get_series(trade.id()).add({"timestamp": trade.timestamp, "inst_id": trade.inst_id, "price": trade.price, "size": trade.size})

    def get_bar(self, inst_id):
        if inst_id in self.__bar_dict:
            return self.__bar_dict[inst_id]
        return None

    def get_quote(self, inst_id):
        if inst_id in self.__quote_dict:
            return self.__quote_dict[inst_id]
        return None

    def get_trade(self, inst_id):
        if inst_id in self.__trade_dict:
            return self.__trade_dict[inst_id]
        return None

    def get_latest_price(self, inst_id):
        if inst_id in self.__trade_dict:
            return self.__trade_dict[inst_id].price
        elif inst_id in self.__quote_dict:
            return self.__quote_dict[inst_id].mid()
        elif inst_id in self.__bar_dict:
            return self.__bar_dict[inst_id].close
        return None

    def get_series(self, key, create_if_missing=True, cls=DataSeries, desc=None, missing_value=np.nan):
        if type(key) == str:
            if key not in self.__series_dict:
                self.__series_dict[key] = cls(name=key, desc=desc, missing_value=missing_value)
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
