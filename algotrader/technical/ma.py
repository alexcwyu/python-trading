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

    def on_update(self, time_value):
        time, value = time_value
        if self.input.size() >= self.length:
            value = 0.0
            for idx in range(self.input.size() - self.length, self.input.size()):
                value += self.input.get_value_by_idx(idx)
            value = round(value / float(self.length), 8)
            self.add(time, value)
        else:
            self.add(time, np.nan)



