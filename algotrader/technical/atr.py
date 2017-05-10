from typing import Dict

from algotrader.technical import Indicator
from algotrader.technical.ma import SMA


class ATR(Indicator):
    __slots__ = (
        'length',
        '__prev_close',
        '__value',
        '__average',
    )

    def __init__(self, time_series=None, inputs=None, input_keys=['high', 'low', 'close'], desc="Average True Range",
                 length=14):
        super(ATR, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  length=length)
        self.length = self.get_int_config("length", 14)
        self.__prev_close = None
        self.__value = None
        self.__average = SMA(inputs=inputs, length=self.length)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        sma_input = {}
        high = data['high']
        low = data['low']
        close = data['close']

        if self.__prev_close is None:
            tr = high - low
        else:
            tr1 = high - low
            tr2 = abs(high - self.__prev_close)
            tr3 = abs(low - self.__prev_close)
            tr = max(max(tr1, tr2), tr3)

        self.__prev_close = close

        sma_input[Indicator.VALUE] = tr
        self.__average.add(timestamp=timestamp, data=sma_input)

        result = {}
        # result['timestamp'] = data['timestamp']
        result[Indicator.VALUE] = self.__average.now(Indicator.VALUE)
        self.add(timestamp=timestamp, data=result)
