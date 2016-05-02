import datetime

import numpy as np

from algotrader.technical import Indicator
from algotrader.utils.time_series import TimeSeries


class Lowest(Indicator):
    _slots__ = (
        'length'
    )

    @staticmethod
    def get_name(input, length):
        return "Lowest(%s,%s)" % (Indicator.get_input_name(input), length)

    def __init__(self, input, length, description="Lowest"):
        super(Lowest, self).__init__(Lowest.get_name(input, length), input, description)
        self.length = int(length)

    def on_update(self, time_value):
        time, value = time_value
        if self.input.size() >= self.length:
            value = 0.0
            lowest = value
            for idx in range(self.input.size() - self.length, self.input.size()):
                lowest = max(lowest,  self.input.get_by_idx(idx))
            self.add(time, lowest)
        else:
            self.add(time, np.nan)



