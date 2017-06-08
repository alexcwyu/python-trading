import numpy as np
from typing import Dict

from algotrader.technical import Indicator


class SMA(Indicator):
    Length = 10
    __slots__ = (
        'length'
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="Simple Moving Average", length=0):
        super(SMA, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  length=length)
        self.length = self.get_int_config("length", SMA.Length)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.first_input.size() >= self.length:
            value = 0.0
            for idx in range(self.first_input.size() - self.length, self.first_input.size()):
                value += self.first_input.get_by_idx(idx, self.first_input_keys)
            value = round(value / float(self.length), 8)
            result[Indicator.VALUE] = value
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)
