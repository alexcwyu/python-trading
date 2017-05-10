import numpy as np
import pandas as pd
from typing import Dict

from algotrader.technical.pipeline import PipeLine


class Rank(PipeLine):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Rank", ascending=True):
        super(Rank, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                   ascending=ascending)

        self.ascending = self.get_bool_config("ascending", True)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        super(Rank, self)._process_update(source=source, timestamp=timestamp, data=data)
        result = {}
        if self.all_filled():
            df = pd.DataFrame(self.cache)
            result[PipeLine.VALUE] = ((df.rank(axis=1, ascending=self.ascending) - 1) / (df.shape[1] - 1)).tail(
                1).values
        else:
            result[PipeLine.VALUE] = self._default_output()

        self.add(timestamp=timestamp, data=result)

    def _default_output(self):
        na_array = np.empty(shape=self.shape())
        na_array[:] = np.nan
        return na_array

    def shape(self):
        return np.array([1, self.numPipes])
