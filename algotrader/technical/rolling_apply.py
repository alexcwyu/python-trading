import math
import numpy as np
from algotrader.technical import Indicator

class RollingApply(Indicator):
    _slots__ = (
        'length',
        'func'
    )

    def __init__(self, input, input_key=None, length=0, func=np.std, desc="Rolling Apply"):
        super(RollingApply, self).__init__(Indicator.get_name(RollingApply.__name__, input, input_key, length), input, input_key, desc)
        self.length = int(length)
        self.func = func
        super(RollingApply, self).update_all()

    def on_update(self, data):
        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            sliced = input.get_by_idx(keys=self.input_keys, idx=slice(-self.length, None, None))
            result[Indicator.VALUE] = self.func(sliced)
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)
