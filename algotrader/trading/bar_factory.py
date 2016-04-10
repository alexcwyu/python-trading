import datetime
from collections import defaultdict

from rx.subjects import Subject

from algotrader.event.market_data import MarketDataEventHandler, Bar, BarType
from algotrader.utils.clock import default_clock


class Subscriable(object):
    _slots__ = (
        'subject',
    )

    def __init__(self):
        self.subject = Subject()

    def on_next(self, value):
        self.subject.on_next(value)


class BarInputType:
    Trade = 1
    Bid = 2
    Ask = 3
    BidAsk = 4
    Middle = 5
    Spread = 6


class BarFactoryItem:
    _slots__ = (
        'type',
        'size',
    )

    def __init__(self, type=BarType.Time, size=60):
        self.type = type
        self.size = size


class BarFactory(Subscriable, MarketDataEventHandler):
    _slots__ = (
        'subject',
        'input',
        'instrument',
        'last_price',
        'last_vol',
        'inst_bar_dict',
        'time_set',
    )

    def __init__(self, input):
        super(BarFactory, self).__init__()
        self.input = input
        self.inst_bar_dict = defaultdict(defaultdict(lambda: None))
        self.time_set = set()



    def on_bar(self, bar):
        self.on_market_data(self, bar.instrument, bar.timestamp, bar.close, bar.vol)

    def on_quote(self, quote):

        if self.input == BarInputType.Bid:
            price = quote.bid
            vol = quote.bid_size

        elif self.input == BarInputType.Ask:
            price = quote.ask
            vol = quote.ask_size
        elif self.input == BarInputType.Middle:
            price = (quote.bid + quote.ask) / 2
            vol = (quote.bid_size + quote.ask_size) / 2
        elif self.input == BarInputType.Spread:
            price = quote.ask = quote.bid
            vol = 0
        elif self.input == BarInputType.BidAsk:
            self.on_market_data(quote.instrument, quote.timestamp, quote.bid, quote.bid_size)
            self.on_market_data(quote.instrument, quote.timestamp, quote.ask, quote.ask_size)

        if price != self.last_price and vol != self.last_vol:
            self.on_market_data(quote.instrument, quote.timestamp, price, vol)
            self.last_price = price
            self.last_vol = vol

    def on_trade(self, trade):
        if self.input == BarInputType.Trade:
            self.on_market_data(trade.instrument.trade.timestamp, trade.price, trade.size)

    def on_market_data(self, instrument, timestamp, price, vol):
        bar_type = (BarType.Time, 60)
        bar = self.inst_bar_dict[instrument][bar_type]

        if bar_type[0] == BarType.Time:
            if not bar:
                bar = Bar(instrument=instrument,
                          type=bar_type[0],
                          size=bar_type[1],
                          timestamp=timestamp,
                          open=price, high=price, low=price, close=price, vol=vol)
                self.inst_bar_dict[instrument][bar_type] = bar

                remind_time = timestamp + datetime.timedelta(0, bar_type[1])
                self.add_reminder(remind_time)
            else:
                bar.timestamp = timestamp
                if price > bar.high:
                    bar.high = price
                if price < bar.low:
                    bar.low = price

                bar.close = price
                bar.vol += vol
        elif bar_type[0] == BarType.Tick:
            if not bar:
                bar = Bar(instrument=instrument,
                          type=bar_type[0],
                          size=1,
                          timestamp=timestamp,
                          open=price, high=price, low=price, close=price, vol=vol)
                self.inst_bar_dict[instrument][bar_type] = bar
            else:
                bar.timestamp = timestamp
                bar.size += 1
                if price > bar.high:
                    bar.high = price
                if price < bar.low:
                    bar.low = price
                bar.close = price
                bar.vol += vol

                if bar.size >= bar_type[1]:
                    self.__emit(instrument, bar_type)

        elif bar_type[0] == BarType.Volume:
            if not bar:
                bar = Bar(instrument=instrument,
                          type=bar_type[0],
                          size=bar_type[1],
                          timestamp=timestamp,
                          open=price, high=price, low=price, close=price, vol=vol)
                self.inst_bar_dict[instrument][bar_type] = bar
            else:
                bar.timestamp = timestamp
                if price > bar.high:
                    bar.high = price
                if price < bar.low:
                    bar.low = price
                bar.close = price
                bar.vol += vol

                if bar.vol >= bar_type[1]:
                    self.__emit(instrument, bar_type)

    def add_reminder(self, time):
        if time not in self.time_set:
            self.time_set.add(time)
            default_clock.add_reminder(self.on_reminder, time)

    def on_reminder(self, time):
        for inst, bar_dict in self.inst_bar_dict.items():
            for bar_type, bar in bar_dict.items():
                if bar and bar_type[0] == BarType.Time:
                    end_time = bar.begin_time + datetime.timedelta(0, bar_type[1])
                    if end_time <= time:
                        self.__emit(inst, bar_type)
        self.time_set.remove(time)

    def __create_bar(self, instrument, type, size, timestamp, price, vol):
        bar = Bar(instrument=instrument,
                  type=type,
                  size=size,
                  timestamp=timestamp,
                  open=price, high=price, low=price, close=price, vol=vol)
        self.inst_bar_dict[instrument][(type, size)] = bar
        return bar

    def __emit(self, instrument, bar_type):

        bar = self.inst_bar_dict[instrument][bar_type]
        self.inst_bar_dict[instrument][bar_type] = None
        # TODO emit
