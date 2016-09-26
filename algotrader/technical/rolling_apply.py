import math
import numpy as np
from algotrader.technical import Indicator

class RollingApply(Indicator):
    _slots__ = (
        'length',
        'func'
    )

    def __init__(self, name, input, input_key=None, length=0, func=np.std, desc="Rolling Apply"):
        super(RollingApply, self).__init__(name, input, input_key, desc)
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


class StdDev(RollingApply):
    def __init__(self, input, input_key='close', length=30, desc="Rolling Standard Deviation"):
        super(StdDev, self).__init__(input, func=lambda x: np.std(x, axis=0),
                                      name=Indicator.get_name(StdDev.__name__, input, input_key),
                                      input_key=input_key, desc=desc)