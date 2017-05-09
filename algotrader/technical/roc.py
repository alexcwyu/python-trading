import numpy as np

from algotrader.technical import Indicator
from typing import Dict


def roc(prev_value, curr_value):
    if prev_value != 0.0:
        return (curr_value - prev_value) / prev_value
    return np.nan


class ROC(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, input=None, input_key=None, length=1, desc="Rate Of Change"):
        self.length = int(length)
        super(ROC, self).__init__(Indicator.get_name(ROC.__name__, input, input_key, length), input, input_key, desc)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.input.size() > self.length:
            prev_value = self.input.ago(self.length, self.input_keys[0])
            curr_value = self.input.now(self.input_keys[0])
            result[Indicator.VALUE] = roc(prev_value, curr_value)
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)
