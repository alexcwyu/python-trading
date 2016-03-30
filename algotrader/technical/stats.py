import numpy as np

from algotrader.technical import Indicator



class MAX(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, length, description="Maximum"):
        super(MAX, self).__init__(input, "MAX(%s,%s)" % (input.name, length), description)
        self.length = length

    def on_update(self, time_value):
        time, value = time_value
        if self.input.size() >= self.length:
            self.add(time, self.input.max(-self.length))
        else:
            self.add(time, np.nan)


class MIN(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, length, description="Minimum"):
        super(MIN, self).__init__(input, "MIN(%s,%s)" % (input.id, length), description)
        self.length = length

    def on_update(self, time_value):
        time, value = time_value
        if self.input.size() >= self.length:
            self.add(time, self.input.min(-self.length))
        else:
            self.add(time, np.nan)


class STD(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, length, description="Standard Deviation"):
        super(STD, self).__init__(input, "STD(%s,%s)" % (input.id, length), description)
        self.length = length

    def on_update(self, time_value):
        time, value = time_value
        if self.input.size() >= self.length:
            self.add(time, self.input.std(-self.length))
        else:
            self.add(time, np.nan)


class VAR(Indicator):
    _slots__ = (
        'length'
    )

    def __init__(self, input, length, description="Variance"):
        super(VAR, self).__init__(input, "VAR(%s,%s)" % (input.id, length), description)
        self.length = length

    def on_update(self, time_value):
        time, value = time_value
        if self.input.size() >= self.length:
            self.add(time, self.input.std(-self.length))
        else:
            self.add(time, np.nan)
