import numpy as np
from typing import Dict

from algotrader.technical.pipeline import PipeLine


class Corr(PipeLine):
    def __init__(self, time_series=None, inputs=None, input_keys='close',
                 desc="Correlation", length=30):
        super(Corr, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                   length=length)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        super(Corr, self)._process_update(source=source, timestamp=timestamp, data=data)
        result = {}
        if self.inputs[0].size() > self.length:
            if self.all_filled():
                result[PipeLine.VALUE] = self.df.corr()
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
        return np.array([self.numPipes, self.numPipes])
