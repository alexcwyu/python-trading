import datetime

from bidict import bidict

from algotrader.model.market_data_pb2 import *
from algotrader.utils.date import datetime_to_unixtimemillis

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

bar_size_map = {
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


def get_bar_size(name: str) -> int:
    return bar_size_map[name]


subscription_type_map = bidict({
    "Bar": MarketDataSubscriptionRequest.Bar,
    "Quote": MarketDataSubscriptionRequest.Quote,
    "Trade": MarketDataSubscriptionRequest.Trade,
    "MarketDepth": MarketDataSubscriptionRequest.MarketDepth
})


def get_subscription_type_name(type: MarketDataSubscriptionRequest.MDType) -> str:
    return subscription_type_map.inv[type]


def get_subscription_type(name: str) -> MarketDataSubscriptionRequest.MDType:
    return subscription_type_map[name]


bar_type_map = bidict({
    "Time": Bar.Time,
    "Tick": Bar.Tick,
    "Volume": Bar.Volume,
    "Dynamic": Bar.Dynamic
})


def get_bar_type_name(type: Bar.Type) -> str:
    return bar_type_map.inv[type]


def get_bar_type(name: str) -> Bar.Type:
    return bar_type_map[name]


def get_next_bar_start_time(timestamp: int, bar_size: int) -> int:
    return get_current_bar_start_time(timestamp, bar_size) + bar_size * 1000


def get_current_bar_end_time(timestamp: int, bar_size: int) -> int:
    return get_next_bar_start_time(timestamp, bar_size) - 1


def get_current_bar_start_time(timestamp: int, bar_size: int) -> int:
    if bar_size < D1:
        return int(timestamp / (bar_size * 1000)) * bar_size * 1000
    else:
        dt = datetime.datetime.fromtimestamp(timestamp / 1000)
        return datetime_to_unixtimemillis(datetime.datetime(year=dt.year, month=dt.month, day=dt.day))


def get_quote_mid(quote: Quote) -> float:
    if quote.bid is not None and quote.bid > 0 and quote.ask is not None and quote.ask > 0:
        return (quote.bid + quote.ask) / 2
    elif quote.bid is not None and quote.bid > 0:
        return quote.bid
    return quote.ask


def get_series_id(item) -> str:
    if isinstance(item, Bar):
        return "Bar.%s.%s.%s" % (item.inst_id, get_bar_type_name(item.type), item.size)
    if isinstance(item, Trade):
        return "Trade.%s" % (item.inst_id)
    if isinstance(item, Quote):
        return "Quote.%s" % (item.inst_id)
    if isinstance(item, MarketDepth):
        return "MarketDepth.%s" % (item.inst_id)

    raise RuntimeError("unknown series type")
