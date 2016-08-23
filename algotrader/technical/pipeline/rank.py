from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine


class Rank(PipeLine):
    _slots__ = (
    )

    def __init__(self, inputs, input_key='close', desc="Rank"):
        super(Rank, self).__init__(Indicator.get_name(Rank.__name__, input),
                                   input,  input_key, desc)

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
