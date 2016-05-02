import datetime

import numpy as np

from algotrader.technical import Indicator
from algotrader.utils.time_series import TimeSeries
from algotrader.event.order import OrdAction


class MAE(Indicator):
    _slots__ = (
        'length',
        'direction'
    )

    @staticmethod
    def get_name(bopen, high, low, bclose, action, length):
        return "M(%s,%s,%s,%s,%s,%s)" % \
               ( Indicator.get_input_name(bopen),
                 Indicator.get_input_name(high),
                 Indicator.get_input_name(low),
                 Indicator.get_input_name(bclose),
                 action, length)

    def __init__(self, bopen, high, low, bclose, action, length, description="MAE"):
        super(MAE, self).__init__(MAE.get_name(bopen, high, low, bclose, length),
                                  bopen, high, low, bclose, description)
        self.length = int(length)
        self.action = action

    def on_update(self, time_value):
        if self.action == OrdAction.BUY:
            time, value = time_value
        if self.input.size() >= self.length:
            value = 0.0
            for idx in range(self.input.size() - self.length, self.input.size()):
                value += self.input.get_by_idx(idx)
            value = round(value / float(self.length), 8)
            self.add(time, value)
        else:
            self.add(time, np.nan)



