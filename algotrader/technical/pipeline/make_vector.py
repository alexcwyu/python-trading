import numpy as np

from algotrader.technical.pipeline import PipeLine


class MakeVector(PipeLine):
    _slots__ = (
    )

    def __init__(self, inputs, input_key='close', desc="Bundle and Sync DataSeries to Vector"):
        super(MakeVector, self).__init__(PipeLine.get_name(MakeVector.__name__, inputs, input_key),
                                         inputs, input_key, length=1, desc=desc)
        super(MakeVector, self).update_all()

    def on_update(self, data):
        super(MakeVector, self).on_update(data)
        result = {}
        result['timestamp'] = data['timestamp']
        if self.inputs[0].size() >= self.length:
            if self.all_filled():
                packed_matrix = np.transpose(np.array(self.cache.values()))
                result[PipeLine.VALUE] = packed_matrix
            else:
                result[PipeLine.VALUE] = self._default_output()
        else:
            result[PipeLine.VALUE] = self._default_output()

        self.add(result)

    def _default_output(self):
        na_array = np.empty(shape=self.shape())
        na_array[:] = np.nan
        return na_array

    def shape(self):
        return np.array([1, self.numPipes])
