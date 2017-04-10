import datetime

from algotrader.model.market_data_pb2 import *
from algotrader.utils.date_utils import DateUtils


class BarSize(object):
    S1 = 1
    S5 = 5
    S15 = 15
    S30 = 30
    M1 = 60
    M5 = 5 * 60
    M15 = 15 * 60
    M30 = 30 * 60
    H1 = 60 * 60
    D1 = 24 * 60 * 60


class BarType(object):
    map = {
        0: "Time",
        1: "Tick",
        2: "Volume",
        3: "Dynamic"
    }

    @staticmethod
    def name(type: int) -> str:
        return BarType.map[type]


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
