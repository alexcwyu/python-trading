import numpy as np

from algotrader.technical import Indicator


class SMA(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, input_key=None, length=0, desc="Simple Moving Average"):
        super(SMA, self).__init__(Indicator.get_name(SMA.__name__, input, input_key, length), input, input_key, desc)
        self.length = int(length)
        super(SMA, self).update_all()

    def on_update(self, data):
        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            value = 0.0
            for idx in range(self.input.size() - self.length, self.input.size()):
                value += self.input.get_by_idx(idx, self.input_keys[0])
            value = round(value / float(self.length), 8)
            result[Indicator.VALUE] = value
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)
