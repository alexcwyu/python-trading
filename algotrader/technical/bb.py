import datetime

import numpy as np

from algotrader.technical import Indicator
from algotrader.utils.time_series import TimeSeries


class BB(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, length=14, description="Bollinger Band"):
        super(BB, self).__init__(input, "BB(%s, %s)" % (input.id, length), description)
        self.length = length

    def on_update(self, time_value):
        pass



