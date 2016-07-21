import math
import numpy as np

from algotrader.technical import Indicator


class HistoricalVolatility(Indicator):
    _slots__ = (
        'length'
        'ann_factor'
    )

    def __init__(self, input, input_key=None, length=0, ann_factor=252, desc="Historical Volatility"):
        super(HistoricalVolatility, self).__init__(Indicator.get_name(HistoricalVolatility.__name__, input, input_key, length), input, input_key, desc)
        self.length = int(length)
        self.ann_factor = ann_factor

    def on_update(self, data):
        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            sum_ret_sq = 0.0
            for idx in range(self.input.size() - self.length+1, self.input.size()):
                x_t = self.input.get_by_idx(idx, self.input_keys[0])
                x_t_1 = self.input.get_by_idx(idx-1, self.input_keys[0])
                ret = math.log(x_t/x_t_1)
                sum_ret_sq += ret**2
            result[Indicator.VALUE] = math.sqrt(self.ann_factor*sum_ret_sq/self.length)
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)
