import datetime

import numpy as np

from algotrader.technical import Indicator
from algotrader.utils.time_series import TimeSeries


class SMA(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, length, description="Simple Moving Average"):
        super(SMA, self).__init__(input, "SMA(%s,%s)" % (input.id, length), description)
        self.length = length

    def on_time_value(self, time_value):
        time, value = time_value
        if self.input.size() >= self.length:
            value = 0.0
            for idx in range(self.input.size() - self.length, self.input.size()):
                value += self.input.get_value_by_idx(idx)
            value = round(value / float(self.length), 8)
            self.add(time, value)
        else:
            self.add(time, np.nan)


def main():
    close = TimeSeries("close")
    sma = SMA(close, 3)

    t1 = datetime.datetime.now()
    t2 = t1 + datetime.timedelta(0, 3)
    t3 = t2 + datetime.timedelta(0, 3)
    t4 = t3 + datetime.timedelta(0, 3)
    t5 = t4 + datetime.timedelta(0, 3)
    print "####"
    print close.get_data()
    print sma.get_data()

    close.add(t1, 2)
    print "####"
    print close.get_data()
    print sma.get_data()

    close.add(t2, 2.4)
    print "####"
    print close.get_data()
    print sma.get_data()

    close.add(t3, 2.8)
    print "####"
    print close.get_data()
    print sma.get_data()

    close.add(t4, 3.2)
    print "####"
    print close.get_data()
    print sma.get_data()
    close.add(t5, 3.6)
    print "####"
    print close.get_data()
    print sma.get_data()


if __name__ == "__main__":
    main()
