import numpy as np

from algotrader.technical import Indicator
from algotrader.technical.ma import SMA
from algotrader.technical.stats import STD
from typing import Dict


class BB(Indicator):
    UPPER = 'uppper'
    LOWER = 'lower'

    __slots__ = (
        'length',
        'num_std'
        '__sma',
        '__std_dev',
    )

    def __init__(self, input=None, input_key=None, length=14, num_std=3, desc="Bollinger Bands"):
        self.length = int(length)
        self.num_std = int(num_std)
        self.__sma = SMA(input, self.length)
        self.__std_dev = STD(input, self.length)
        super(BB, self).__init__(Indicator.get_name(BB.__name__, input, input_key, length, num_std), input, input_key,
                                 desc)

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
