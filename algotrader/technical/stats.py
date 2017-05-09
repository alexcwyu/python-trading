import numpy as np

from algotrader.technical import Indicator
from typing import Dict


class MAX(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, input=None, input_key=None, length=0, desc="Maximum"):
        self.length = int(length)
        super(MAX, self).__init__(Indicator.get_name(MAX.__class__, input, input_key, length), input, input_key,
                                  desc)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.input.size() >= self.length:
            result[Indicator.VALUE] = self.input.max(-self.length, self.input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)


class MIN(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, input, input_key=None, length=0, desc="Minimum"):
        super(MIN, self).__init__(Indicator.get_name(MIN.__class__, input, input_key, length), input, input_key,
                                  desc)
        self.length = int(length)
        super(MIN, self)._update_from_inputs()

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.input.size() >= self.length:
            result[Indicator.VALUE] = self.input.min(-self.length, self.input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)


class STD(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, input, input_key=None, length=0, desc="Standard Deviation"):
        super(STD, self).__init__(Indicator.get_name(STD.__class__, input, input_key, length), input, input_key,
                                  desc)
        self.length = int(length)
        super(STD, self)._update_from_inputs()

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.input.size() >= self.length:
            result[Indicator.VALUE] = self.input.std(-self.length, self.input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)


class VAR(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, input, input_key=None, length=0, desc="Variance"):
        super(VAR, self).__init__(Indicator.get_name(VAR.__class__, input, input_key, length), input, input_key,
                                  desc)
        self.length = int(length)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.input.size() >= self.length:
            result[Indicator.VALUE] = self.input.std(-self.length, self.input_keys[0])
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)
