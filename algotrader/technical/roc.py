import numpy as np
from typing import Dict

from algotrader.technical import Indicator


def roc(prev_value, curr_value):
    if prev_value != 0.0:
        return (curr_value - prev_value) / prev_value
    return np.nan


class ROC(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="Rate Of Change", length=1):
        super(ROC, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  length=length)
        self.length = self.get_int_config("length", 1)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.input_series[0].size() > self.length:
            prev_value = self.input_series[0].ago(self.length, self.get_input_keys(self.input_series[0].name))
            curr_value = self.input_series[0].now(self.get_input_keys(self.input_series[0].name))
            result[Indicator.VALUE] = roc(prev_value, curr_value)
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)
