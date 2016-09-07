from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
import numpy as np


class Rank(PipeLine):
    _slots__ = (
        'ascending'
    )

    def __init__(self, inputs, ascending=True, input_key='close', desc="Rank"):
        super(Rank, self).__init__(PipeLine.get_name(Rank.__name__, inputs, input_key),
                                   inputs, input_key, length=1, desc=desc)
        self.ascending = ascending
        super(Rank, self).update_all()

    def on_update(self, data):
        super(Rank, self).on_update(data)
        result = {}
        result['timestamp'] = data['timestamp']
        if self.all_filled():
            result[PipeLine.VALUE] = ((self.df.rank(axis=1, ascending=self.ascending) - 1)/(self.df.shape[1]-1)).head(1).values
        else:
            result[PipeLine.VALUE] = self._default_output()

        self.add(result)

    def _default_output(self):
        na_array = np.empty(shape=self.shape())
        na_array[:] = np.nan
        return na_array

    def shape(self):
        return np.array([1, self.numPipes])
