from rx.subjects import Subject

from algotrader.event.market_data import MarketDataEventHandler, BarType, BarSize, Quote, Trade, Bar
from algotrader.trading.bar_factory import BarInputType
from algotrader.utils.time_series import DataSeries
import datetime
from rx.observable import Observable
class BarAggregator(MarketDataEventHandler):
    def __init__(self, data_bus, clock, inst_data_mgr, inst_id, input,
                 input_type=BarInputType.Trade,
                 output_bar_type=BarType.Time,
                 output_size=BarSize.M1):
        self.__data_bus = data_bus
        self.__clock = clock
        self.__inst_id = inst_id
        self.__input_type = input_type
        self.__output_bar_type = output_bar_type
        self.__output_size = output_size
        if isinstance(input, DataSeries):
            self.__input = input
        else:
            self.__input = inst_data_mgr.get_series(input)

        self.__timestamp = clock.now()
        self.__reset()

    def start(self):
        self.__input.subject.subscribe(on_next=self.on_update)
        if self.__output_bar_type == BarType.Time:
            current_ts = self.__clock.now()
            next_ts = Bar.get_next_bar_start_time(current_ts, BarSize.S5)
            diff = next_ts - current_ts
            Observable.timer(int(diff), self.__output_size * 1000, self.__clock.scheduler).subscribe(on_next=self.publish)


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
        self.set_value(bar['timestamp'], bar['open'], bar['high'], bar['low'], bar['close'], bar['vol'])

    def on_quote(self, quote):
        value = 0
        size = 0
        if self.__input_type == BarInputType.Ask:
            value = quote['ask']
            size = quote['ask_size']
        if self.__input_type == BarInputType.Bid:
            value = quote['bid']
            size = quote['bid_size']
        if self.__input_type == BarInputType.BidAsk:
            value = quote['bid'] if quote['bid'] > 0 else quote['ask']
            size = quote['bid_size'] if quote['bid'] > 0 else quote['ask_size']
        if self.__input_type == BarInputType.Middle:
            value = (quote['ask'] + quote['bid']) / 2
            size = int((quote['ask_size'] + quote['bid_size']) / 2)

        self.set_value(quote['timestamp'], value, value, value, value, size)

    def on_trade(self, trade):
        value = trade['price']
        size = trade['size']

        self.set_value(trade['timestamp'], value, value, value, value, size)

    def set_value(self, timestamp, open, high, low, close, size):
        self.publish();
        if self.__new_bar:
            self.__start_time = timestamp
            if self.__output_bar_type == BarType.Time:
                self.__end_time = Bar.get_current_bar_end_time(timestamp, self.__output_size)
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
        if self.__output_bar_type == BarType.Time:
            bar_end_time = Bar.get_current_bar_end_time(self.__clock.now() + 100, self.__output_size)
            if self.__timestamp >= self.__end_time or bar_end_time >= self.__end_time:
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

        ## Tick Bar
        if self.__output_bar_type == BarType.Tick and self.__count >= self.__output_size:
            self.publish()

        ## Vol Bar
        if self.__output_bar_type == BarType.Volume and self.__volume >= self.__output_size:
            residual = self.__volume - self.__output_size if self.__output_bar_type == BarType.Volume else 0
            self.publish()
            if residual:
                func(data)
                self.__volume = residual

    def publish(self, *args):

        if self.__count > 0:
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


data_feed = Subject()

aggregator = BarAggregator()
