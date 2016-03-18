from algotrader.event import *
import abc

from atom.api import Atom, Unicode, Range, Bool, observe, Enum, Str, Value, Float, Long, Int


class Frequency(object):
    S = 1
    M1 = 60
    M5 = 5 * 60
    M30 = 30 * 60
    H1 = 60 * 60
    H4 = 4 * 60 * 60
    D1 = 24 * 60 * 60


class MarketDataEvent(Event):
    instrument = Str()
    timestamp = Value(current_time)


class Bar(MarketDataEvent):
    freq = Long()
    open = Float()
    high = Float()
    low = Float()
    close = Float()
    vol = Float()
    adj_close = Float()

    # __slots__ = (
    #     'freq',
    #     'open',
    #     'high',
    #     'low',
    #     'close',
    #     'vol',
    #     'adj_close'
    # )
    #
    # def __init__(self, instrument, timestamp, open, high, low, close, vol, adj_close, freq=Frequency.D1):
    #     super(self.__class__, self).__init__(instrument, timestamp)
    #     self.freq = freq
    #     self.open = open
    #     self.high = high
    #     self.low = low
    #     self.close = close
    #     self.vol = vol
    #     self.adj_close = adj_close

    def __str__(self):
        return "Bar(instrument = %s, timestamp = %s,freq = %s, open = %s, high = %s, low = %s, close = %s, vol = %s, adj_close = %s)" \
               % (self.instrument, self.timestamp, self.freq, self.open, self.high, self.low, self.close, self.vol,
                  self.adj_close)

    def on(self, handler):
        handler.on_bar(self)

    def close_or_adj_close(self):
        #return self.adj_close if self.adj_close > 0 else self.close
        return self.close


class Trade(MarketDataEvent):
    price = Float()
    size = Long()

    #
    # __slots__ = (
    #     'price',
    #     'size'
    # )
    #
    # def __init__(self, instrument, timestamp, price, size):
    #     super(self.__class__, self).__init__(instrument, timestamp)
    #     self.price = price
    #     self.size = size

    def __str__(self):
        return "Trade(instrument = %s, timestamp = %s,price = %s, size = %s)" \
               % (self.instrument, self.timestamp, self.price, self.size)

    def on(self, handler):
        handler.on_trade(self)


class Quote(MarketDataEvent):
    bid = Float()
    bid_size = Long()
    ask = Float()
    ask_size = Long()

    #
    # __slots__ = (
    #     'bid',
    #     'bid_size',
    #     'ask',
    #     'ask_size',
    # )
    #
    # def __init__(self, instrument, timestamp, bid, bid_size, ask, ask_size):
    #     super(self.__class__, self).__init__(instrument, timestamp)
    #     self.bid = bid
    #     self.bid_size = bid_size
    #     self.ask = ask
    #     self.ask_size = ask_size

    def __str__(self):
        return "Quote(instrument = %s, timestamp = %s,bid = %s, bid_size = %s, ask = %s, ask_size = %s)" \
               % (self.instrument, self.timestamp, self.bid, self.bid_size, self.ask, self.ask_size)

    def on(self, handler):
        handler.on_quote(self)

    def mid(self):
        if self.bid > 0 and self.ask > 0:
            return (self.bid + self.ask) / 2
        elif self.bid > 0:
            return self.bid
        return self.ask


class MarketDataEventHandler(EventHandler):
    def on_bar(self, bar):
        pass

    def on_quote(self, quote):
        pass

    def on_trade(self, trade):
        pass
