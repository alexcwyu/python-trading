import datetime
from collections import defaultdict

from rx.subjects import Subject

from algotrader.event import EventBus
from algotrader.event.market_data import MarketDataEventHandler, Bar, BarType, BarSize
from algotrader.utils.clock import default_clock


class Subscribable(object):
    _slots__ = (
        'subject',
    )

    def __init__(self):
        self.subject = Subject()

    def publish(self, value):
        self.subject.on_next(value)


class BarInputType:
    Bar = 0
    Trade = 1
    Bid = 2
    Ask = 3
    BidAsk = 4
    Middle = 5
    Spread = 6


class BarRequest:
    _slots__ = (
        'instrument',
        'input_type',
        'input_size',
        'output_type',
        'output_size',
    )

    def __init__(self, instrument, input_type=BarInputType.Trade, input_size=None, output_type=BarType.Time,
                 output_size=BarSize.M1):
        self.instrument = instrument
        self.input_type = input_type
        self.input_size = input_size
        self.output_type = output_type
        self.output_size = output_size


class BarFactory(Subscribable, MarketDataEventHandler):
    _slots__ = (

        'input_subject',
        'output_subject',
        'requests',
        'inst_bar_dict',
        'inst_price_vol',
        'time_set',
    )

    def __init__(self, input_subject=None, output_subject=None):
        super(BarFactory, self).__init__()

        if not input_subject:
            input_subject = EventBus.data_subject
        self.input_subject = input_subject

        if not output_subject:
            output_subject = EventBus.data_subject
        self.output_subject = output_subject

        self.requests = defaultdict(lambda: defaultdict(set))
        self.inst_bar_dict = defaultdict(lambda: defaultdict(lambda: None))
        self.inst_price_vol = dict()
        self.time_set = set()

        input_subject.subscribe(self.on_next)

    def add_request(self, instrument, input_type=BarInputType.Trade, input_size=None, output_type=BarType.Time,
                    output_size=BarSize.M1):
        if input_type == 'Quote' or input_type == 'Trade':
            input_size = None
        self.requests[instrument][(input_type, input_size)].add((output_type, output_size))

    def on_bar(self, bar):
        if bar.instrument in self.requests and ('Bar', bar.size) in self.requests[bar.instrument]:
            for type, size in self.requests[bar.instrument][('Bar', bar.size)]:
                print "OK %s" % bar
                self.update(type, size, bar.instrument, bar.timestamp, bar.close, bar.vol)

        else:
            print "ignore %s" % bar

    def on_quote(self, quote):

        if quote.instrument in self.requests and ('Quote', None) in self.requests[quote.instrument]:
            for type, size in self.requests[quote.instrument][('Quote', None)]:
                if type == BarInputType.BidAsk:
                    self.update(type, size, quote.instrument, quote.timestamp, quote.bid, quote.bid_size)
                    self.update(type, size, quote.instrument, quote.timestamp, quote.ask, quote.ask_size)
                else:
                    if type == BarInputType.Bid:
                        price = quote.bid
                        vol = quote.bid_size

                    elif type == BarInputType.Ask:
                        price = quote.ask
                        vol = quote.ask_size
                    elif type == BarInputType.Middle:
                        price = (quote.bid + quote.ask) / 2
                        vol = (quote.bid_size + quote.ask_size) / 2
                    elif type == BarInputType.Spread:
                        price = quote.ask - quote.bid
                        vol = 0

                    last_data = self.inst_price_vol.get(quote.instrument, None)
                    last_price = last_data[0] if last_data else 0
                    last_vol = last_data[1] if last_data else 0

                    if price != last_price and vol != last_vol:
                        self.inst_price_vol[quote.instrument] = (price, vol)
                        self.update(type, size, quote.instrument, quote.timestamp, price, vol)

    def on_trade(self, trade):
        if trade.instrument in self.requests and ('Trade', None) in self.requests[trade.instrument]:
            for type, size in self.requests[trade.instrument][('Trade', None)]:
                self.update(type, size, trade.instrument.trade.timestamp, trade.price, trade.size)

    def update(self, type, size, instrument, timestamp, price, vol):
        bar = self.inst_bar_dict[instrument][(type, size)]

        if type == BarType.Time:

            if not bar:
                bar = Bar(instrument=instrument,
                          type=type,
                          size=size,
                          timestamp=timestamp,
                          begin_time= timestamp,
                          open=price, high=price, low=price, close=price, vol=vol)
                self.inst_bar_dict[instrument][(type, size)] = bar

                remind_time = timestamp + datetime.timedelta(0, size)
                self.add_reminder(remind_time)
            else:


                bar.timestamp = timestamp
                if price > bar.high:
                    bar.high = price
                if price < bar.low:
                    bar.low = price

                bar.close = price
                bar.vol += vol
        elif type == BarType.Tick:
            if not bar:
                bar = Bar(instrument=instrument,
                          type=type,
                          size=1,
                          timestamp=timestamp,
                          begin_time= timestamp,
                          open=price, high=price, low=price, close=price, vol=vol)
                self.inst_bar_dict[instrument][(type, size)] = bar
            else:

                bar.timestamp = timestamp
                bar.size += 1
                if price > bar.high:
                    bar.high = price
                if price < bar.low:
                    bar.low = price
                bar.close = price
                bar.vol += vol

                if bar.size >= size:
                    self.__emit(instrument, (type, size))

        elif type == BarType.Volume:
            if not bar:
                bar = Bar(instrument=instrument,
                          type=type,
                          size=size,
                          timestamp=timestamp,
                          begin_time= timestamp,
                          open=price, high=price, low=price, close=price, vol=vol)
                self.inst_bar_dict[instrument][(type, size)] = bar
            else:
                bar.timestamp = timestamp
                if price > bar.high:
                    bar.high = price
                if price < bar.low:
                    bar.low = price
                bar.close = price
                bar.vol += vol

                if bar.vol >= size:
                    self.__emit(instrument, (type, size))

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
        bar = Bar(instrument="%s*****" %instrument,
                  type=type,
                  size=size,
                  timestamp=timestamp,
                  open=price, high=price, low=price, close=price, vol=vol)
        self.inst_bar_dict[instrument][(type, size)] = bar
        return bar

    def __emit(self, instrument, bar_type):

        bar = self.inst_bar_dict[instrument][bar_type]
        self.inst_bar_dict[instrument][bar_type] = None
        if bar:
            self.output_subject.on_next(bar)
