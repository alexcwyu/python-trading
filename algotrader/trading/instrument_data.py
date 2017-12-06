import numpy as np

from algotrader import Manager, Context
from algotrader.model.model_factory import ModelFactory
from algotrader.model.market_data_pb2 import *
from algotrader.model.time_series_pb2 import *
from algotrader.provider.datastore import PersistenceMode
# from algotrader.trading.data_series import DataSeries
from algotrader.trading.event import MarketDataEventHandler
from algotrader.trading.series import Series
from algotrader.trading.data_frame import DataFrame
from algotrader.utils.logging import logger
from algotrader.utils.market_data import get_series_id, get_frame_id
from algotrader.utils.model import get_full_cls_name, get_cls
from algotrader.utils.protobuf_to_dict import protobuf_to_dict
from algotrader.app import Application


class InstrumentDataManager(MarketDataEventHandler, Manager):
    def __init__(self):
        super(InstrumentDataManager, self).__init__()
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}
        self.__series_dict = {}
        self.__transient_series_dict = {}
        self.__frame_dict = {}
        self.__transient_frame_dict = {}
        self.subscription = None
        self.store = None

    def _start(self, app_context: Context) -> None:
        self.store = app_context.get_data_store()
        self.persist_mode = app_context.config.get_app_config("persistenceMode")
        self.load_all()
        self.subscription = app_context.event_bus.data_subject.subscribe(self.on_market_data_event)

    def _stop(self):
        if self.subscription:
            self.subscription.dispose()
        self.save_all()
        self.reset()

    def load_all(self):
        if self.store:
            self.store.start(self.app_context)
            # proto_series_list = self.store.load_all('series')
            # for ps in proto_series_list:
            #     series = Series.from_proto_series(ps)
            #     self.__series_dict[series.series_id] = series
            #
            # proto_frame_list = self.store.load_all("frame")
            # for bd in proto_frame_list:
            #     df = DataFrame.from_proto_frame(bd, app_context=self.app_context)
            #     self.__frame_dict[df.df_id] = df

            bars = self.store.load_all("bars")
            for bar in bars:
                self.__bar_dict[get_series_id(bar)] = bar

            trades = self.store.load_all("trades")
            for trade in trades:
                self.__trade_dict[get_series_id(trade)] = trade

            quotes = self.store.load_all("quotes")
            for quote in quotes:
                self.__quote_dict[get_series_id(quote)] = quote

    def save_all(self):
        if self.store:
            if self.persist_mode == PersistenceMode.Batch:
                for bar in self.__bar_dict.values():
                    self.store.save_bar(bar)
                for quote in self.__quote_dict.values():
                    self.store.save_quote(quote)
                for trade in self.__trade_dict.values():
                    self.store.save_trade(trade)

            elif self.persist_mode != PersistenceMode.Disable:
                for series in self.__series_dict.values():
                    self.store.save_series(series.to_proto_series())

                for df in self.__frame_dict.values():
                    self.store.save_frame(df.to_proto_frame(self.app_context))

    def _is_realtime_persist(self):
        return self.store and self.persist_mode == PersistenceMode.RealTime

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__bar_dict[bar.inst_id] = bar
        app_type = self.app_context.config.config['Application']['type']
        transient = True if app_type == Application.BackTesting else False

        cols_series_id = {'close': get_series_id(bar, tags='close', provider_id=bar.provider_id),
                        'open': get_series_id(bar, tags='open', provider_id=bar.provider_id),
                        'high': get_series_id(bar, tags='high', provider_id=bar.provider_id),
                        'low': get_series_id(bar, tags='low', provider_id=bar.provider_id),
                        'volume': get_series_id(bar, tags='volume', provider_id=bar.provider_id)
                        }

        self.get_series(get_series_id(bar, tags='close', provider_id=bar.provider_id), transient=transient).add(
            timestamp=bar.timestamp,
            value=bar.close)

        self.get_series(get_series_id(bar, tags='open', provider_id=bar.provider_id), transient=transient).add(
            timestamp=bar.timestamp,
            value=bar.open)

        self.get_series(get_series_id(bar, tags='high', provider_id=bar.provider_id), transient=transient).add(
            timestamp=bar.timestamp,
            value=bar.high)

        self.get_series(get_series_id(bar, tags='low', provider_id=bar.provider_id), transient=transient).add(
            timestamp=bar.timestamp,
            value=bar.low)

        self.get_series(get_series_id(bar, tags='volume', provider_id=bar.provider_id), transient=transient).add(
            timestamp=bar.timestamp,
            value=bar.volume)

        self.get_frame(
            get_frame_id(bar,
                         provider_id=bar.provider_id),
            provider_id=bar.provider_id,
            inst_id=bar.inst_id,
            columns=['close', 'open', 'high', 'low', 'volume'],
            cols_series_id=cols_series_id,
            transient=transient
        ).append_row(
            index=bar.timestamp,
            value=protobuf_to_dict(bar)
        )

        if self._is_realtime_persist():
            self.store.save_bar(bar)

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__quote_dict[quote.inst_id] = quote

        self.get_series(get_series_id(quote)).add(
            timestamp=quote.timestamp,
            value={"bid": quote.bid, "ask": quote.ask, "bid_size": quote.bid_size,
                   "ask_size": quote.ask_size})

        if self._is_realtime_persist():
            self.store.save_quote(quote)

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__trade_dict[trade.inst_id] = trade
        self.get_series(get_series_id(trade)).add(
            timestamp=trade.timestamp,
            value={"price": trade.price, "size": trade.size})

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

    def get_series(self, key, df_id=None, col_id=None, inst_id=None, transient=False):
        if transient:
            return self._get_transient_series(key, df_id, col_id, inst_id)
        else:
            return self._get_series(key, df_id, col_id, inst_id)

    def _get_transient_series(self, key, df_id=None, col_id=None, inst_id=None):
        if type(key) != str:
            raise AssertionError()

        if key not in self.__transient_series_dict:
            series = Series(series_id=key, df_id=df_id, col_id=col_id, inst_id=inst_id, dtype=np.float64)
            self.__transient_series_dict[key] = series
            series.start(self.app_context)
        return self.__transient_series_dict[key]

    def _get_series(self, key, df_id=None, col_id=None, inst_id=None):
        if type(key) != str:
            raise AssertionError()

        if key not in self.__series_dict:
            if self.store.obj_exist('series', key):
                proto_series = self.store.load_one('series', key)
                series = Series.from_proto_series(proto_series)
            else:
                series = Series(series_id=key, df_id=df_id, col_id=col_id, inst_id=inst_id, dtype=np.float64)

            series.start(self.app_context)
            self.__series_dict[key] = series
        return self.__series_dict[key]

    def add_series(self, series, raise_if_duplicate=False):
        if series.series_id not in self.__series_dict:
            self.__series_dict[series.series_id] = series
            if self._is_realtime_persist():
                self.store.save_series(series.to_proto_series())
        elif raise_if_duplicate and self.__series_dict[series.series_id] != series:
            raise AssertionError("Series [%s] already exist" % series.series_id)

    def get_frame(self, key, provider_id=None, inst_id=None, columns=None, cols_series_id : dict = None, transient=False):
        if transient:
            return self._get_transient_frame(key, provider_id, inst_id, columns, cols_series_id)
        else:
            return self._get_frame(key, provider_id, inst_id, columns, cols_series_id)

    def _get_transient_frame(self, key, provider_id=None, inst_id=None, columns=None, cols_series_id : dict = None):
        if type(key) != str:
            raise AssertionError()

        if key not in self.__transient_frame_dict:
            if cols_series_id:
                series_dict = {k: self.get_series(v, transient=True) for k, v in cols_series_id.items()}
                frame = DataFrame.from_series_dict(series_dict)
            else:
                frame = DataFrame(df_id=key, provider_id=provider_id, inst_id=inst_id, columns=columns)
            self.__transient_frame_dict[key] = frame
            frame.start(self.app_context)
        return self.__transient_frame_dict[key]

    def _get_frame(self, key, provider_id=None, inst_id=None, columns=None, cols_series_id : dict = None):
        if isinstance(key, str):
            if key not in self.__frame_dict:
                if self.store.obj_exist('frame', key):
                    proto_frame = self.store.load_one('frame', key)
                    frame = DataFrame.from_proto_frame(proto_frame, app_context=self.app_context)
                else:
                    if cols_series_id:
                        series_dict = {k: self.get_series(v, transient=False) for k, v in cols_series_id.items()}
                        frame = DataFrame.from_series_dict(series_dict)
                    else:
                        frame = DataFrame(df_id=key, provider_id=provider_id, inst_id=inst_id, columns=columns)

                frame.start(self.app_context)
                self.__frame_dict[key] = frame

            return self.__frame_dict[key]

    def add_frame(self, df: DataFrame, raise_if_duplicate=True):
        if df.df_id not in self.__frame_dict:
            self.__frame_dict[df.df_id] = df
            if self._is_realtime_persist():
                self.store.save_frame(df.to_proto_frame(self.app_context))
        elif raise_if_duplicate and self.__frame_dict[df.df_id] != df:
            raise AssertionError("Dataframe [%s] already exist" % df.df_id)

    def has_series(self, name):
        return name in self.__series_dict

    def has_frame(self, name):
        return name in self.__frame_dict

    def reset(self):
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}
        self.__series_dict = {}
        self.__frame_dict = {}

    def id(self):
        return "InstrumentDataManager"
