from rx import Observable

from algotrader.event.event_handler import MarketDataEventHandler
from algotrader.model.model_factory import *
from algotrader.provider.subscription import *
from algotrader.trading.data_series import DataSeries
from algotrader.utils import logger


class BarInputType:
    Bar = 0
    Trade = 1
    Bid = 2
    Ask = 3
    BidAsk = 4
    Middle = 5
    Spread = 6


class BarAggregator(MarketDataEventHandler):
    def __init__(self, data_bus, clock, inst_id, input,
                 input_type=BarInputType.Trade,
                 output_bar_type=Bar.Time,
                 output_size=BarSize.M1):
        self.__data_bus = data_bus
        self.__clock = clock
        self.__inst_id = inst_id
        self.__input_type = input_type
        self.__output_bar_type = output_bar_type
        self.__output_size = output_size

        if isinstance(input, DataSeries):
            self.__input = input
            self.__input_name = input.name
        else:
            self.__input = None
            self.__input_name = input.name

        self.__timestamp = clock.now()
        self.__reset()

    def _start(self, app_context, **kwargs):
        if self.__input is None:
            self.__input = app_context.inst_data_mgr.get_series(self.__input_name)
        self.__input.subject.subscribe(on_next=self.on_update)
        if self.__output_bar_type == Bar.Time:
            current_ts = self.__clock.now()
            next_ts = Bar.get_next_bar_start_time(current_ts, self.__output_size)
            diff = next_ts - current_ts
            Observable.timer(int(diff), self.__output_size * 1000, self.__clock.scheduler).subscribe(
                on_next=self.publish)

    def __reset(self):
        self.__new_bar = True
        self.__start_time = 0
        self.__end_time = 0
        self.__open = 0
        self.__high = 0
        self.__low = 0
        self.__close = 0
        self.__count = 0
        self.__volume = 0

    def on_bar(self, bar):
        self.set_value(bar.get('timestamp', None), bar.get('open', None), bar.get('high', None), bar.get('low', None),
                       bar.get('close', None), bar.get('vol', 0))

    def on_quote(self, quote):
        value = 0
        size = 0
        if self.__input_type == BarInputType.Ask:
            value = quote.get('ask', None)
            size = quote.get('ask_size', 0)
        if self.__input_type == BarInputType.Bid:
            value = quote.get('bid', None)
            size = quote.get('bid_size', 0)
        if self.__input_type == BarInputType.BidAsk:
            if quote.get('bid', 0) > 0 and quote.get('bid_size', 0) > 0:
                value = quote.get('bid', None)
                size = quote.get('bid_size', 0)
            else:
                value = quote.get('ask', None)
                size = quote.get('ask_size', 0)
        if self.__input_type == BarInputType.Middle:
            value = (quote['ask'] + quote['bid']) / 2 if 'bid' in quote and 'ask' in quote else None
            size = int((quote.get('ask_size', 0) + quote.get('bid_size', 0)) / 2)

        self.set_value(quote.get('timestamp', None), value, value, value, value, size)

    def on_trade(self, trade):
        value = trade.get('price', None)
        size = trade.get('size', 0)

        self.set_value(trade.get('timestamp', None), value, value, value, value, size)

    def set_value(self, timestamp, open, high, low, close, size):
        if timestamp is None or close is None:
            logger.warning("[%s] ignore update timestamp=%s, open=%s, high=%s, low=%s, close=%s, size=%s" % (
                self.__class__.__name__, timestamp, open, high, low, close, size))
            return
        if self.__new_bar:

            if self.__output_bar_type == Bar.Time:
                self.__start_time = Bar.get_current_bar_start_time(timestamp, self.__output_size)
                self.__end_time = Bar.get_current_bar_end_time(timestamp, self.__output_size)
            else:
                self.__start_time = timestamp
            self.__open = open
            self.__low = low
            self.__high = high
            self.__new_bar = False
        else:
            if high > self.__high:
                self.__high = high
            if low < self.__low:
                self.__low = low

        self.__count += 1
        self.__close = close
        self.__volume += size

    def on_update(self, data):
        if isinstance(data, (Trade, Bar, Quote)):
            data = data.to_dict()

        self.__timestamp = data['timestamp']

        ## Time Bar, need to check if require publish existing before handling new update
        if self.__output_bar_type == Bar.Time and self.__count > 0 and self.__timestamp > self.__end_time:
            self.publish()

        if self.__input_type == BarInputType.Bar:
            func = self.on_bar
        elif (self.__input_type == BarInputType.Ask
              or self.__input_type == BarInputType.Bid
              or self.__input_type == BarInputType.BidAsk
              or self.__input_type == BarInputType.Middle):
            func = self.on_quote
        elif self.__input_type == BarInputType.Trade:
            func = self.on_trade
        else:
            raise Exception

        func(data)

        ## Time Bar
        if self.__output_bar_type == Bar.Time and self.__count > 0 and self.__timestamp >= self.__end_time:
            self.publish()

        ## Tick Bar
        elif self.__output_bar_type == Bar.Tick and self.__count >= self.__output_size:
            self.publish()

        ## Vol Bar
        elif self.__output_bar_type == Bar.Volume:
            while self.__volume >= self.__output_size:
                residual = self.__volume - self.__output_size
                self.__volume = self.__output_size
                self.publish()
                if residual:
                    func(data)
                    self.__volume = residual

    def publish(self, *args):

        if self.__count > 0:

            if self.__output_bar_type == Bar.Time:
                self.__timestamp = self.__end_time

            bar = Bar(inst_id=self.__inst_id,
                      begin_time=self.__start_time,
                      timestamp=self.__timestamp,
                      open=self.__open,
                      high=self.__high,
                      low=self.__low,
                      close=self.__close,
                      vol=self.__volume,
                      adj_close=0,
                      size=self.__output_size,
                      type=self.__output_bar_type)
            self.__data_bus.on_next(bar)
            self.__reset()

    def count(self):
        return self.__count

    def id(self):
        return "%s.%s.%s.%s.%s" % (
            self.__inst_id, self.__input_name, self.__input_type, self.__output_bar_type, self.__output_size)
