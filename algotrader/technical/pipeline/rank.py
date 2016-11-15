from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
import numpy as np
import pandas as pd
from algotrader.utils import logger


class Rank(PipeLine):
    __slots__ = (
        'ascending'
    )

    def __init__(self, inputs=None, ascending=True, input_key='close', desc="Rank"):
        self.ascending = ascending
        super(Rank, self).__init__(PipeLine.get_name(Rank.__name__, inputs, input_key),
                                   inputs, input_key, length=1, desc=desc)
        # super(Rank, self).update_all()

    def on_update(self, data):
        super(Rank, self).on_update(data)
        result = {}
        result['timestamp'] = data['timestamp']
        if self.all_filled():
            df = pd.DataFrame(self.cache)
            result[PipeLine.VALUE] = ((df.rank(axis=1, ascending=self.ascending) - 1)/(df.shape[1]-1)).tail(1).values.tolist()
        else:
            result[PipeLine.VALUE] = self._default_output()

        self.add(result)

    def _default_output(self):
        na_array = np.empty(shape=self.shape())
        na_array[:] = np.nan
        return na_array.tolist()

    def shape(self):
        return [1, self.numPipes]
