import numpy as np

from algotrader.technical import Indicator


class MAX(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, input_key=None, length=0, desc="Maximum"):
        super(MAX, self).__init__(Indicator.get_name(MAX.__class__, input, input_key, length), input, input_key,
                                  desc)
        self.length = int(length)

    def on_update(self, data):
        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            result[Indicator.VALUE] = self.input.max(-self.length, self.input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)


class MIN(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, input_key=None, length=0, desc="Minimum"):
        super(MIN, self).__init__(Indicator.get_name(MIN.__class__, input, input_key, length), input, input_key,
                                  desc)
        self.length = int(length)

    def on_update(self, data):
        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            result[Indicator.VALUE] = self.input.min(-self.length, self.input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)


class STD(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, input_key=None, length=0, desc="Standard Deviation"):
        super(STD, self).__init__(Indicator.get_name(STD.__class__, input, input_key, length), input, input_key,
                                  desc)
        self.length = int(length)

    def on_update(self, data):
        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            result[Indicator.VALUE] = self.input.std(-self.length, self.input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)


class VAR(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, input_key=None, length=0, desc="Variance"):
        super(VAR, self).__init__(Indicator.get_name(VAR.__class__, input, input_key, length), input, input_key,
                                  desc)
        self.length = int(length)

    def on_update(self, data):
        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            result[Indicator.VALUE] = self.input.std(-self.length, self.input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)
