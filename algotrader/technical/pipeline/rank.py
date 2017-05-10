import numpy as np
import pandas as pd
from typing import Dict

from algotrader.model.time_series_pb2 import TimeSeriesUpdateEvent
from algotrader.technical.pipeline import PipeLine


class Rank(PipeLine):
    _slots__ = (
        'ascending'
    )

    def __init__(self, inputs, ascending=True, input_key='close', desc="Rank"):
        self.ascending = ascending
        super(Rank, self).__init__(PipeLine.get_name(Rank.__name__, inputs, input_key),
                                   inputs, input_key, length=1, desc=desc)
        # super(Rank, self).update_all()

    def on_update(self, event: TimeSeriesUpdateEvent):
        super(Rank, self).on_update(event)
        self._process_update(event.source, event.item.timestamp, event.item.data)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
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
