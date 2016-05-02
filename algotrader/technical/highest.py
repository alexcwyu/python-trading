import datetime

import numpy as np

from algotrader.technical import Indicator
from algotrader.utils.time_series import TimeSeries


class Highest(Indicator):
    _slots__ = (
        'length'
    )

    @staticmethod
    def get_name(input, length):
        return "Highest(%s,%s)" % (Indicator.get_input_name(input), length)

    def __init__(self, input, length, description="Highest"):
        super(Highest, self).__init__(Highest.get_name(input, length), input, description)
        self.length = int(length)

    def on_update(self, time_value):
        time, value = time_value
        if self.input.size() >= self.length:
            value = 0.0
            highest = value
            for idx in range(self.input.size() - self.length, self.input.size()):
                highest = max(highest,  self.input.get_by_idx(idx))
            self.add(time, highest)
        else:
            self.add(time, np.nan)



