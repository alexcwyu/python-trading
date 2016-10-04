import datetime

from algotrader.event.event import Event
from algotrader.utils.date_utils import DateUtils


class MarketDataType(object):
    Bar = 'Bar'
    Quote = 'Quote'
    Trade = 'Trade'
    MarketDepth = 'MarketDepth'


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


class BarType:
    Time = 1
    Tick = 2
    Volume = 3
    Dynamic = 4

    map = {
        1: "Time",
        2: "Tick",
        3: "Volume",
        4: "Dynamic"
    }

    @staticmethod
    def name(type):
        return BarType.map[type]


class MDSide:
    Ask = 0
    Bid = 1


class MDOperation:
    Insert = 0
    Update = 1
    Delete = 2


class MarketDataEvent(Event):
    __slots__ = (
        'inst_id',
    )

    def __init__(self, inst_id, timestamp):
        super(MarketDataEvent, self).__init__(timestamp)
        self.inst_id = inst_id

    def series_id(self):
        raise NotImplementedError()

    def id(self):
        return "%s-%s" % (self.series_id(), self.timestamp)


class Bar(MarketDataEvent):
    __slots__ = (
        'type',
        'size',
        'begin_time',
        'open',
        'high',
        'low',
        'close',
        'vol',
        'adj_close'
    )

    def __init__(self, inst_id=None, begin_time=0, timestamp=None, open=0, high=0, low=0, close=0, vol=0,
                 adj_close=0,
                 size=BarSize.D1, type=BarType.Time):
        super(Bar, self).__init__(inst_id, timestamp)
        self.type = type
        self.size = size
        self.begin_time = begin_time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.vol = vol
        self.adj_close = adj_close

    def series_id(self):
        return "Bar.%s.%s.%s" % (self.inst_id, BarType.name(self.type), self.size)

    def on(self, handler):
        handler.on_bar(self)

    def close_or_adj_close(self):
        return self.close

    def to_dict(self, all_data=False):
        data = {"timestamp": self.timestamp, "open": self.open, "high": self.high, "low": self.low, "close": self.close,
                "vol": self.vol}

        if all_data:
            data['begin_time'] = self.begin_time
            data['inst_id'] = self.inst_id
            data['type'] = self.type
            data['size'] = self.size
            data['adj_close'] = self.adj_close

        return data

    def save(self, data_store):
        data_store.save_bar(self)

    @staticmethod
    def get_next_bar_start_time(timestamp, bar_size):
        return Bar.get_current_bar_start_time(timestamp, bar_size) + bar_size * 1000

    @staticmethod
    def get_current_bar_end_time(timestamp, bar_size):
        return Bar.get_next_bar_start_time(timestamp, bar_size) - 1

    @staticmethod
    def get_current_bar_start_time(timestamp, bar_size):
        if bar_size < BarSize.D1:
            return int(timestamp / (bar_size * 1000)) * bar_size * 1000
        else:
            dt = datetime.datetime.fromtimestamp(timestamp / 1000)
            return DateUtils.datetime_to_unixtimemillis(datetime.datetime(year=dt.year, month=dt.month, day=dt.day))


class Trade(MarketDataEvent):
    __slots__ = (
        'price',
        'size'
    )

    def __init__(self, inst_id=None, timestamp=None, price=0, size=0):
        super(Trade, self).__init__(inst_id, timestamp)
        self.price = price
        self.size = size

    def series_id(self):
        return "Trade.%s" % (self.inst_id)

    def on(self, handler):
        handler.on_trade(self)

    def to_dict(self, all_data=False):
        data = {"timestamp": self.timestamp, "price": self.price, "size": self.size}

        if all_data:
            data['inst_id'] = self.inst_id

        return data

    def save(self, data_store):
        data_store.save_trade(self)


class Quote(MarketDataEvent):
    __slots__ = (
        'bid',
        'bid_size',
        'ask',
        'ask_size',
    )

    def __init__(self, inst_id=None, timestamp=None, bid=0, bid_size=0, ask=0, ask_size=0):
        super(Quote, self).__init__(inst_id, timestamp)
        self.bid = bid
        self.bid_size = bid_size
        self.ask = ask
        self.ask_size = ask_size

    def series_id(self):
        return "Quote.%s" % (self.inst_id)

    def on(self, handler):
        handler.on_quote(self)

    def mid(self):
        if self.bid > 0 and self.ask > 0:
            return (self.bid + self.ask) / 2
        elif self.bid > 0:
            return self.bid
        return self.ask

    def to_dict(self, all_data=False):
        data = {"timestamp": self.timestamp, "bid": self.bid, "ask": self.ask, "bid_size": self.bid_size,
                "ask_size": self.ask_size}
        if all_data:
            data['inst_id'] = self.inst_id
        return data

    def save(self, data_store):
        data_store.save_quote(self)


class MarketDepth(MarketDataEvent):
    __slots__ = (
        'provider_id',
        'position',
        'operation',
        'side',
        'price',
        'size',
    )

    def __init__(self, inst_id=None, timestamp=None, provider_id=None, position=0, operation=None, side=None,
                 price=0.0, size=0):
        super(MarketDepth, self).__init__(inst_id, timestamp)
        self.provider_id = provider_id
        self.position = position
        self.operation = operation
        self.side = side
        self.price = price
        self.size = size

    def series_id(self):
        return "MarketDepth.%s" % (self.inst_id)

    def on(self, handler):
        handler.on_market_depth(self)

    def save(self, data_store):
        data_store.save_market_depth(self)
