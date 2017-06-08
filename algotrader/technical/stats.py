import numpy as np
from typing import Dict

from algotrader.technical import Indicator


class MAX(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="Maximum", length=0):
        super(MAX, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  length=length)
        self.length = self.get_int_config("length", 0)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.self.first_input.size() >= self.length:
            result[Indicator.VALUE] = self.self.first_input.max(-self.length, self.first_input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)


class MIN(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="Minimum", length=0):
        super(MIN, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  length=length)
        self.length = self.get_int_config("length", 0)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.first_input.size() >= self.length:
            result[Indicator.VALUE] = self.first_input.min(-self.length, self.first_input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)


class STD(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="Standard Deviation", length=0):
        super(STD, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  length=length)
        self.length = self.get_int_config("length", 0)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.first_input.size() >= self.length:
            result[Indicator.VALUE] = self.first_input.std(-self.length, self.first_input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)


class VAR(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="Variance", length=0):
        super(VAR, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  length=length)
        self.length = self.get_int_config("length", 0)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.first_input.size() >= self.length:
            result[Indicator.VALUE] = self.first_input.std(-self.length, self.first_input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)
