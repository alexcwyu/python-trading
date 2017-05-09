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

    def __init__(self, input=None, length=14, desc="Average True Range"):
        self.length = int(length)
        self.__prev_close = None
        self.__value = None
        self.__average = SMA(input, self.length)
        super(ATR, self).__init__(Indicator.get_name(ATR.__name__, input, length), input, ['high', 'low', 'close'],
                                  desc)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        sma_input = {}
        # sma_input['timestamp'] = event.timestamp
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
        self.add(timestamp=event.timestamp, data=result)
