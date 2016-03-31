import numpy as np

from algotrader.technical import Indicator
from algotrader.utils.time_series import TimeSeries


class MAX(Indicator):
    _slots__ = (
        'length'
    )

    @staticmethod
    def get_name(cls, input, length):
        return "MAX(%s,%s)" % (Indicator.get_input_name(input), length)

    def __init__(self, input, length, description="Maximum"):
        super(MAX, self).__init__(MAX.get_name(input, length), input, description)
        self.length = int(length)

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

    @staticmethod
    def get_name(cls, input, length):
        return "MIN(%s,%s)" % (Indicator.get_input_name(input), length)

    def __init__(self, input, length, description="Minimum"):
        super(MIN, self).__init__(MIN.get_name(input, length), input, description)
        self.length = int(length)

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

    @staticmethod
    def get_name(cls, input, length):
        return "STD(%s,%s)" % (Indicator.get_input_name(input), length)

    def __init__(self, input, length, description="Standard Deviation"):
        super(STD, self).__init__(STD.get_name(input, length), input, description)
        self.length = int(length)

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

    @staticmethod
    def get_name(cls, input, length):
        return "VAR(%s,%s)" % (Indicator.get_input_name(input), length)

    def __init__(self, input, length, description="Variance"):
        super(VAR, self).__init__(VAR.get_name(input, length), input, description)
        self.length = int(length)

    def on_update(self, time_value):
        time, value = time_value
        if self.input.size() >= self.length:
            self.add(time, self.input.std(-self.length))
        else:
            self.add(time, np.nan)
