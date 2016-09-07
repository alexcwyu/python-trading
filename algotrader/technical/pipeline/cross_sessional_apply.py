from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
import numpy as np

#TODO: One output scalar
#TODO: Output Vector Apply class

class CrossSessionalApply(PipeLine):
    _slots__ = (
        'np_func'
    )

    def __init__(self, inputs, np_func, input_key='close', length=30, desc="Cross Sessional Apply"):
        super(CrossSessionalApply, self).__init__(PipeLine.get_name(CrossSessionalApply.__name__, input),
                                   input,  input_key, length, desc)
        self.np_func = np_func
        super(CrossSessionalApply, self).update_all()

    def on_update(self, data):
        super(CrossSessionalApply, self).on_update(data)
        result = {}
        result['timestamp'] = data['timestamp']
        if self.inputs[0].size() > self.length:
            if self.all_filled():
                result[PipeLine.VALUE] = self.np_func(self.df.values)
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
        return np.array([self.numPipes, self.numPipes])



class CrossSessionalApplyScala(PipeLine):
    _slots__ = (
        'np_func'
    )

    def __init__(self, inputs, np_func, input_key='close', length=30, desc="Cross Sessional Apply"):
        super(CrossSessionalApplyScala, self).__init__(PipeLine.get_name(CrossSessionalApplyScala.__name__, inputs, input_key),
                                                       inputs, input_key, length=1, desc=desc)
        self.np_func = np_func
        super(CrossSessionalApplyScala, self).update_all()

    def on_update(self, data):
        super(CrossSessionalApplyScala, self).on_update(data)
        result = {}
        result['timestamp'] = data['timestamp']
        if self.inputs[0].size() > self.length:
            if self.all_filled():
                result[PipeLine.VALUE] = self.np_func(self.df.values)
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
        return np.array([1,1])

class Average(CrossSessionalApplyScala):
    def __init__(self, inputs, input_key='close', desc="Cross Sessional Average"):
        super(Average, self).__init__(inputs=inputs, np_func=np.average, input_key=input_key, length=1, desc=desc)



class Sum(CrossSessionalApplyScala):
    def __init__(self, inputs, input_key='close', desc="Cross Sessional Sum"):
        super(Sum, self).__init__(inputs=inputs, np_func=np.sum, input_key=input_key, length=1, desc=desc)


#TODO: Add Count , Abs, Sum,

