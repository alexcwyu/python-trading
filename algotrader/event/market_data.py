from algotrader.event import *
import abc


class Frequency(object):
    S = 1
    M1 = 60
    M5 = 5 * 60
    M30 = 30 * 60
    H1 = 60 * 60
    H4 = 4 * 60 * 60
    D1 = 24 * 60 * 60


class MarketDataEvent(Event):
    __slots__ = (
        'symbol',
        'timestamp',
    )

    def __init__(self, symbol, timestamp):
        self.symbol = symbol
        self.timestamp = timestamp


class MarketDataEventHandler(EventHandler):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def on_bar(self, bar):
        pass

    @abc.abstractmethod
    def on_quote(self, quote):
        pass

    @abc.abstractmethod
    def on_trade(self, trade):
        pass


class Bar(MarketDataEvent):
    __slots__ = (
        'freq',
        'open',
        'high',
        'low',
        'close',
        'vol',
        'adj_close'
    )

    def __init__(self, symbol, timestamp, open, high, low, close, vol, adj_close, freq=Frequency.D1):
        super(self.__class__, self).__init__(symbol, timestamp)
        self.freq = freq
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.vol = vol
        self.adj_close = adj_close

    def __str__(self):
        return "Bar(symbol = %s, timestamp = %s,freq = %s, open = %s, high = %s, low = %s, close = %s, vol = %s, adj_close = %s)" \
               % (self.symbol, self.timestamp, self.freq, self.open, self.high, self.low, self.close, self.vol,
                  self.adj_close)

    def on(self, handler):
        handler.on_bar(self)


class Trade(MarketDataEvent):
    __slots__ = (
        'price',
        'size'
    )

    def __init__(self, symbol, timestamp, price, size):
        super(self.__class__, self).__init__(symbol, timestamp)
        self.price = price
        self.size = size

    def __str__(self):
        return "Trade(symbol = %s, timestamp = %s,price = %s, size = %s)" \
               % (self.symbol, self.timestamp, self.price, self.size)

    def on(self, handler):
        handler.on_trade(self)


class Quote(MarketDataEvent):
    __slots__ = (
        'bid',
        'bid_size',
        'ask',
        'ask_size',
    )

    def __init__(self, symbol, timestamp, bid, bid_size, ask, ask_size):
        super(self.__class__, self).__init__(symbol, timestamp)
        self.bid = bid
        self.bid_size = bid_size
        self.ask = ask
        self.ask_size = ask_size

    def __str__(self):
        return "Quote(symbol = %s, timestamp = %s,bid = %s, bid_size = %s, ask = %s, ask_size = %s)" \
               % (self.symbol, self.timestamp, self.bid, self.bid_size, self.ask, self.ask_size)

    def on(self, handler):
        handler.on_quote(self)
