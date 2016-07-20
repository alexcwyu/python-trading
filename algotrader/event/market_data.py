from algotrader.event.event import Event, EventHandler

from algotrader.utils import logger
import datetime


class MarketDataEventHandler(EventHandler):
    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))

    def on_market_depth(self, market_depth):
        logger.debug("[%s] %s" % (self.__class__.__name__, market_depth))


class BarSize(object):
    S1 = 1
    S5 = 5
    S15 = 15
    S30 = 30
    M1 = 60
    M2 = 120
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

    def id(self):
        raise NotImplementedError()


from algotrader.utils.clock import Clock
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

    def __init__(self, inst_id=None, begin_time=None, timestamp=None, open=0, high=0, low=0, close=0, vol=0,
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

    def id(self):
        return "Bar.%s.%s.%s" % (self.inst_id, BarType.name(self.type), self.size)

    def __str__(self):
        return "Bar(inst_id = %s, begin_time = %s, timestamp = %s,type = %s, size = %s, open = %s, high = %s, low = %s, close = %s, vol = %s, adj_close = %s)" \
               % (
                   self.inst_id, self.begin_time, self.timestamp, self.type, self.size, self.open, self.high, self.low,
                   self.close, self.vol,
                   self.adj_close)

    def on(self, handler):
        handler.on_bar(self)

    def close_or_adj_close(self):
        # return self.adj_close if self.adj_close > 0 else self.close
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
            dt = datetime.datetime(year=dt.year, month=dt.month, day=dt.day)
            next_ts = Clock.datetime_to_unixtimemillis(dt)
            return next_ts


class Trade(MarketDataEvent):
    __slots__ = (
        'price',
        'size'
    )

    def __init__(self, inst_id=None, timestamp=None, price=0, size=0):
        super(Trade, self).__init__(inst_id, timestamp)
        self.price = price
        self.size = size

    def id(self):
        return "Trade.%s" % (self.inst_id)

    def __str__(self):
        return "Trade(inst_id = %s, timestamp = %s,price = %s, size = %s)" \
               % (self.inst_id, self.timestamp, self.price, self.size)

    def on(self, handler):
        handler.on_trade(self)

    def to_dict(self, all_data=False):
        data = {"timestamp": self.timestamp, "price": self.price, "size": self.size}

        if all_data:
            data['inst_id'] = self.inst_id

        return data


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

    def id(self):
        return "Quote.%s" % (self.inst_id)

    def __str__(self):
        return "Quote(inst_id = %s, timestamp = %s,bid = %s, bid_size = %s, ask = %s, ask_size = %s)" \
               % (self.inst_id, self.timestamp, self.bid, self.bid_size, self.ask, self.ask_size)

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

    def id(self):
        return "MarketDepth.%s" % (self.inst_id)

    def __str__(self):
        return "MarketDepth(inst_id = %s, timestamp = %s, provider_id = %s, position = %s, operation = %s, side = %s, price = %s, size = %s)" \
               % (
                   self.inst_id, self.timestamp, self.provider_id, self.position, self.operation, self.side, self.price,
                   self.size)

    def on(self, handler):
        handler.on_market_depth(self)
