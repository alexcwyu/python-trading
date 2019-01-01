import numpy as np
from typing import Dict

from algotrader.technical.pipeline import PipeLine


class MakeVector(PipeLine):
    def __init__(self, time_series=None, inputs=None, input_keys='close',
                 desc="Bundle and Sync DataSeries to Vector"):
        super(MakeVector, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                         length=1)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        super(MakeVector, self)._process_update(source=source, timestamp=timestamp, data=data)
        result = {}
        if self.get_input(0).size() >= self.length:
            if self.all_filled():
                packed_matrix = np.transpose(np.array(self.cache.values()))
                result[PipeLine.VALUE] = packed_matrix
            else:
                result[PipeLine.VALUE] = self._default_output()
        else:
            result[PipeLine.VALUE] = self._default_output()

        self.add(timestamp=timestamp, data=result)

    def _default_output(self):
        na_array = np.empty(shape=self.shape())
        na_array[:] = np.nan
        return na_array

    def shape(self):
        return np.array([1, self.numPipes])
