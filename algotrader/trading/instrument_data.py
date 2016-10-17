import numpy as np

from algotrader import Manager
from algotrader.config.persistence import PersistenceMode
from algotrader.event.event_bus import EventBus
from algotrader.event.event_handler import MarketDataEventHandler
from algotrader.utils import logger
from algotrader.utils.time_series import DataSeries


class InstrumentDataManager(MarketDataEventHandler, Manager):
    def __init__(self):
        super(InstrumentDataManager, self).__init__()
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}
        self.__series_dict = {}
        self.subscription = None

    def _start(self, app_context, **kwargs):
        self.store = self.app_context.get_timeseries_data_store()
        self.persist_mode = self.app_context.app_config.persistence_config.ts_persist_mode
        self.load_all()
        self.subscription = EventBus.data_subject.subscribe(self.on_next)

    def _stop(self):
        if self.subscription:
            self.subscription.dispose()
        self.save_all()
        self.reset()

    def load_all(self):
        if hasattr(self, "store") and self.store:
            self.store.start(self.app_context)
            series_list = self.store.load_all('time_series')
            for series in series_list:
                self.__series_dict[series.id()] = series

            bars = self.store.load_all('bars')
            for bar in bars:
                self.__bar_dict[bar.id()] = bar

            trades = self.store.load_all('trades')
            for trade in trades:
                self.__trade_dict[trade.id()] = trade

            quotes = self.store.load_all('quotes')
            for quote in quotes:
                self.__quote_dict[quote.id()] = quote

    def save_all(self):
        if hasattr(self, "store") and self.store and self.persist_mode == PersistenceMode.Batch:
            for bar in self.__bar_dict.values():
                self.store.save_bar(bar)
            for quote in self.__quote_dict.values():
                self.store.save_quote(quote)
            for trade in self.__trade_dict.values():
                self.store.save_trade(trade)

        if hasattr(self, "store") and self.store and self.persist_mode != PersistenceMode.Disable:
            for series in self.__series_dict.values():
                self.store.save_time_series(series)

    def _is_realtime_persist(self):
        return hasattr(self, "store") and self.store and self.persist_mode == PersistenceMode.RealTime

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__bar_dict[bar.inst_id] = bar

        self.get_series(bar.series_id()).add(
            {"timestamp": bar.timestamp, "open": bar.open, "high": bar.high, "low": bar.low, "close": bar.close,
             "vol": bar.vol})

        if self._is_realtime_persist():
            self.store.save_bar(bar)

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__quote_dict[quote.inst_id] = quote

        self.get_series(quote.series_id()).add(
            {"timestamp": quote.timestamp, "bid": quote.bid, "ask": quote.ask, "bid_size": quote.bid_size,
             "ask_size": quote.ask_size})

        if self._is_realtime_persist():
            self.store.save_quote(quote)

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__trade_dict[trade.inst_id] = trade
        self.get_series(trade.series_id()).add({"timestamp": trade.timestamp, "price": trade.price, "size": trade.size})

        if self._is_realtime_persist():
            self.store.save_trade(trade)

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

    def add_series(self, series, raise_if_duplicate=False):
        if series.name not in self.__series_dict:
            self.__series_dict[series.name] = series
            if self._is_realtime_persist():
                self.store.save_time_series(series)
        elif raise_if_duplicate and self.__series_dict[series.name] != series:
            raise AssertionError("Series [%s] already exist" % series.name)

    def has_series(self, name):
        return name in self.__series_dict

    def reset(self):
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}
        self.__series_dict = {}

    def id(self):
        return "InstrumentDataManager"
