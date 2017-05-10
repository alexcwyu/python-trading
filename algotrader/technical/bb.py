import numpy as np
from typing import Dict

from algotrader.technical import Indicator
from algotrader.technical.ma import SMA
from algotrader.technical.stats import STD


class BB(Indicator):
    UPPER = 'uppper'
    LOWER = 'lower'

    __slots__ = (
        'length',
        'num_std'
        '__sma',
        '__std_dev',
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="Bollinger Bands", length=14, num_std=3):
        super(SMA, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  length=length, num_std=num_std)
        self.length = self.get_int_config("length", 14)
        self.num_std = self.get_int_config("num_std", 3)
        self.__sma = SMA(inputs=inputs, length=self.length)
        self.__std_dev = STD(inputs=inputs, length=self.length)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        sma = self.__sma.now(self.input_keys[0])
        std = self.__std_dev.now(self.input_keys[0])
        if not np.isnan(sma):
            upper = sma + std * self.num_std
            lower = sma - std * self.num_std

            result[BB.UPPER] = upper
            result[BB.LOWER] = lower
            result[Indicator.VALUE] = sma
        else:
            result[BB.UPPER] = np.nan
            result[BB.LOWER] = np.nan
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)
