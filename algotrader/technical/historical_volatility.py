import math

import numpy as np
from typing import Dict

from algotrader.technical import Indicator


class HistoricalVolatility(Indicator):
    __slots__ = (
        'length'
        'ann_factor'
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="Historical Volatility", length=0, ann_factor=252):
        super(HistoricalVolatility, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  length=length,ann_factor=ann_factor)
        self.length = self.get_int_config("length", 0)
        self.ann_factor = self.get_int_config("ann_factor", 252)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.first_input.size() >= self.length:
            sum_ret_sq = 0.0
            for idx in range(self.first_input.size() - self.length + 1, self.first_input.size()):
                x_t = self.first_input.get_by_idx(idx, self.first_input_keys[0])
                x_t_1 = self.first_input.get_by_idx(idx - 1, self.first_input_keys[0])
                ret = math.log(x_t / x_t_1)
                sum_ret_sq += ret ** 2
            result[Indicator.VALUE] = math.sqrt(self.ann_factor * sum_ret_sq / self.length)
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)
