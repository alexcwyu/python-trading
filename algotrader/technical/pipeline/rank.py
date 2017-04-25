import numpy as np
import pandas as pd

from algotrader.technical.pipeline import PipeLine
from algotrader.trading.data_series import DataSeriesEvent


class Rank(PipeLine):
    _slots__ = (
        'ascending'
    )

    def __init__(self, inputs, ascending=True, input_key='close', desc="Rank"):
        self.ascending = ascending
        super(Rank, self).__init__(PipeLine.get_name(Rank.__name__, inputs, input_key),
                                   inputs, input_key, length=1, desc=desc)
        # super(Rank, self).update_all()

    def on_update(self, event: DataSeriesEvent):
        super(Rank, self).on_update(event)
        result = {}
        result['timestamp'] = event.timestamp
        if self.all_filled():
            df = pd.DataFrame(self.cache)
            result[PipeLine.VALUE] = ((df.rank(axis=1, ascending=self.ascending) - 1) / (df.shape[1] - 1)).tail(
                1).values
        else:
            result[PipeLine.VALUE] = self._default_output()

        self.add(result)

    def _default_output(self):
        na_array = np.empty(shape=self.shape())
        na_array[:] = np.nan
        return na_array

    def shape(self):
        return np.array([1, self.numPipes])
