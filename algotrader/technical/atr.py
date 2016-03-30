from algotrader.event.market_data import Bar
from algotrader.technical import Indicator
from algotrader.technical.ma import SMA


class ATR(Indicator):
    _slots__ = (
        'length',
        '__prev_close',
        '__value',
        '__average',
    )

    def __init__(self, input, length=14, description="Average True Range"):
        super(ATR, self).__init__(input, "ATR(%s, %s)" % (input.name, length), description)
        self.length = length
        self.__prev_close = None
        self.__value = None
        self.__average = SMA(input, length)

    def on_update(self, time_value):
        time, bar = time_value
        assert isinstance(bar, Bar)

        if self.__prev_close is None:
            tr = bar.high - bar.low
        else:
            tr1 = bar.high - bar.low
            tr2 = abs(bar.high - self.__prev_close)
            tr3 = abs(bar.low - self.__prev_close)
            tr = max(max(tr1, tr2), tr3)

        self.__prev_close = bar.close
        self.__average.add(time, tr)
        self.add(time, self.__average.now())

