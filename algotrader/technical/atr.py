from algotrader.technical import Indicator
from algotrader.technical.ma import SMA


class ATR(Indicator):
    _slots__ = (
        'length',
        '__prev_close',
        '__value',
        '__average',
    )

    def __init__(self, input, length=14, desc="Average True Range"):
        super(ATR, self).__init__(Indicator.get_name(ATR.__name__, input, length), input, ['high', 'low', 'close'],
                                  desc)
        self.length = int(length)
        self.__prev_close = None
        self.__value = None
        self.__average = SMA(input, self.length)
        super(ATR, self).update_all()

    def on_update(self, data):
        sma_input = {}
        sma_input['timestamp'] = data['timestamp']
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
        self.__average.add(sma_input)

        result = {}
        result['timestamp'] = data['timestamp']
        result[Indicator.VALUE] = self.__average.now(Indicator.VALUE)
        self.add(result)
