import datetime

from bidict import bidict

from algotrader.model.market_data_pb2 import *
from algotrader.utils.date_utils import DateUtils


class BarSize(object):
    S1 = 1
    S5 = 5
    S15 = 15
    S30 = 30
    M1 = 60
    M5 = 5 * M1
    M15 = 15 * M1
    M30 = 30 * M1
    H1 = 60 * M1
    H4 = 4 * H1
    D1 = 24 * H1

    map = {
        "S1": S1,
        "S5": S5,
        "S15": S15,
        "S30": S30,
        "S1": M1,
        "S1": M5,
        "S1": M15,
        "M30": M30,
        "H1": H1,
        "H4": H4,
        "D1": D1,

        str(S1): S1,
        str(S5): S5,
        str(S15): S15,
        str(S30): S30,
        str(S1): M1,
        str(S1): M5,
        str(S1): M15,
        str(M30): M30,
        str(H1): H1,
        str(H4): H4,
        str(D1): D1
    }

    @staticmethod
    def value(name: str) -> int:
        return BarSize.map[name]

class MarketDataSubscriptionType(object):
    map = bidict({
        "Bar": MarketDataSubscriptionRequest.Bar,
        "Quote": MarketDataSubscriptionRequest.Quote,
        "QuoTradete": MarketDataSubscriptionRequest.Trade,
        "MarketDepth": MarketDataSubscriptionRequest.MarketDepth
    })

    @staticmethod
    def name(type: MarketDataSubscriptionRequest.MDType) -> str:
        return MarketDataSubscriptionType.map.inv[type]

    @staticmethod
    def type(name: str) -> MarketDataSubscriptionRequest.MDType:
        return MarketDataSubscriptionType.map[name]


class BarType(object):
    map = bidict({
        "Time": Bar.Time,
        "Tick": Bar.Tick,
        "Volume": Bar.Volume,
        "Dynamic": Bar.Dynamic
    })

    @staticmethod
    def name(type: Bar.Type) -> str:
        return BarType.map.inv[type]

    @staticmethod
    def type(name: str) -> Bar.Type:
        return BarType.map[name]


class MarketDataUtils(object):
    @staticmethod
    def get_next_bar_start_time(timestamp, bar_size):
        return MarketDataUtils.get_current_bar_start_time(timestamp, bar_size) + bar_size * 1000

    @staticmethod
    def get_current_bar_end_time(timestamp, bar_size):
        return MarketDataUtils.get_next_bar_start_time(timestamp, bar_size) - 1

    @staticmethod
    def get_current_bar_start_time(timestamp, bar_size):
        if bar_size < BarSize.D1:
            return int(timestamp / (bar_size * 1000)) * bar_size * 1000
        else:
            dt = datetime.datetime.fromtimestamp(timestamp / 1000)
            return DateUtils.datetime_to_unixtimemillis(datetime.datetime(year=dt.year, month=dt.month, day=dt.day))

    @staticmethod
    def get_mid(quote: Quote):
        if quote.bid is not None and quote.bid > 0 and quote.ask is not None and quote.ask > 0:
            return (quote.bid + quote.ask) / 2
        elif quote.bid is not None and quote.bid > 0:
            return quote.bid
        return quote.ask

    @staticmethod
    def get_series_id(item) -> str:
        if isinstance(item, Bar):
            return "Bar.%s.%s.%s" % (item.inst_id, BarType.name(item.type), item.size)
        if isinstance(item, Trade):
            return "Trade.%s" % (item.inst_id)
        if isinstance(item, Quote):
            return "Quote.%s" % (item.inst_id)
        if isinstance(item, MarketDepth):
            return "MarketDepth.%s" % (item.inst_id)

        raise RuntimeError("unknown series type")
