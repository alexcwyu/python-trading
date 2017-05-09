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
        if self.input_series[0].size() >= self.length:
            value = 0.0
            for idx in range(self.input_series[0].size() - self.length, self.input_series[0].size()):
                value += self.input_series[0].get_by_idx(idx, self.get_input_keys(self.input_series[0].name))
            value = round(value / float(self.length), 8)
            result[Indicator.VALUE] = value
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)
