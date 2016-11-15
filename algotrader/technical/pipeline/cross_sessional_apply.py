from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
import numpy as np
import pandas as pd

#TODO: One output scalar
#TODO: Output Vector Apply class

class CrossSessionalApply(PipeLine):
    _slots__ = (
        'np_func'
    )

    def __init__(self, inputs, np_func, name, input_key='close', length=30, desc="Cross Sessional Apply"):
        super(CrossSessionalApply, self).__init__(name, inputs,  input_key, length, desc)
        self.np_func = np_func
        super(CrossSessionalApply, self).update_all()

    def on_update(self, data):
        super(CrossSessionalApply, self).on_update(data)
        result = {}
        result['timestamp'] = data['timestamp']
        if self.inputs[0].size() >= self.length:
            if self.all_filled():
                # result[PipeLine.VALUE] = self.np_func(self.df.values)
                packed_matrix = np.transpose(np.array(self.cache.values()))
                # TODO review this if this correctly handle higher dimension array stored in cache
                if len(packed_matrix.shape) == 3:
                    packed_matrix = packed_matrix[:,0,:]
                # TODO what if the cache value is a higher dimension matrix?
                result[PipeLine.VALUE] = self.np_func(packed_matrix).tolist()
            else:
                result[PipeLine.VALUE] = self._default_output()
        else:
            result[PipeLine.VALUE] = self._default_output()

        self.add(result)

    def _default_output(self):
        na_array = np.empty(shape=self.shape())
        na_array[:] = np.nan
        return na_array.tolist()

    def shape(self):
        return [self.numPipes, self.numPipes]



class CrossSessionalApplyScala(PipeLine):
    _slots__ = (
        'np_func'
    )

    def __init__(self, inputs, np_func, name, input_key='close', length=30, desc="Cross Sessional Apply"):
        super(CrossSessionalApplyScala, self).__init__(name, inputs, input_key, length=1, desc=desc)
        self.np_func = np_func
        super(CrossSessionalApplyScala, self).update_all()

    def on_update(self, data):
        super(CrossSessionalApplyScala, self).on_update(data)
        result = {}
        result['timestamp'] = data['timestamp']
        if self.inputs[0].size() >= self.length:
            if self.all_filled():
                packed_matrix = np.transpose(np.array(self.cache.values()))
                # TODO review this if this correctly handle higher dimension array stored in cache
                if len(packed_matrix.shape) == 3:
                    packed_matrix = packed_matrix[:,0,:]
                # TODO what if the cache value is a higher dimension matrix?
                result[PipeLine.VALUE] = self.np_func(packed_matrix).tolist()
                # result[PipeLine.VALUE] = self.np_func(self.df.values)
            else:
                result[PipeLine.VALUE] = self._default_output()
        else:
            result[PipeLine.VALUE] = self._default_output()

        self.add(result)

    def _default_output(self):
        na_array = np.empty(shape=self.shape())
        na_array[:] = np.nan
        return na_array.tolist()

    def shape(self):
        return [1, 1]

class Average(CrossSessionalApplyScala):
    def __init__(self, inputs, input_key='close', desc="Cross Sessional Average"):
        super(Average, self).__init__(inputs=inputs, np_func=np.average,
                                      name=PipeLine.get_name(Average.__name__, inputs, input_key),
                                      input_key=input_key, length=1, desc=desc)



class Sum(CrossSessionalApplyScala):
    def __init__(self, inputs, input_key='close', desc="Cross Sessional Sum"):
        super(Sum, self).__init__(inputs=inputs, np_func=np.sum,
                                  name=PipeLine.get_name(Sum.__name__, inputs, input_key),
                                  input_key=input_key, length=1, desc=desc)


#TODO: Add Count , Abs, Sum,

class Abs(CrossSessionalApply):
    def __init__(self, inputs, input_key='close', desc="Cross Sessional Abs"):
        super(Abs, self).__init__(inputs=inputs, np_func=np.abs,
                                      name=PipeLine.get_name(Abs.__name__, inputs, input_key),
                                      input_key=input_key, length=1, desc=desc)


def np_assign_on_mask(x, lb, ub, newval):
    x[np.logical_and(x > lb, x < ub)] = newval
    return x

def np_sign_to_value(x):
    x[x>0] = 1
    x[x<0] = -1
    return x

def sign_power(x, e):
    return np_sign_to_value(x)*np.power(x, e)

def timeseries_rank_helper(x, ascending):
    df = pd.DataFrame(x)
    return ((df.rank(axis=0, ascending=ascending) - 1)/(df.shape[0]-1)).tail(1).values


class Tail(CrossSessionalApply):
    def __init__(self, inputs, lb, ub, newval, input_key='close', desc="Cross Sessional Tail"):
        super(Tail, self).__init__(inputs=inputs, np_func=lambda x: np_assign_on_mask(x, lb, ub, newval),
                                      name=PipeLine.get_name(Tail.__name__, inputs, input_key),
                                      input_key=input_key, length=1, desc=desc)

class Sign(CrossSessionalApply):
    def __init__(self, inputs, input_key='close', desc="Cross Sessional Sign"):
        super(Sign, self).__init__(inputs=inputs, np_func=lambda x: np_sign_to_value(x),
                                      name=PipeLine.get_name(Sign.__name__, inputs, input_key),
                                      input_key=input_key, length=1, desc=desc)

class Log(CrossSessionalApply):
    def __init__(self, inputs, input_key='close', desc="Cross Sessional Log"):
        super(Log, self).__init__(inputs=inputs, np_func=lambda x: np.log(x),
                                      name=PipeLine.get_name(Log.__name__, inputs, input_key),
                                      input_key=input_key, length=1, desc=desc)

class Scale(CrossSessionalApply):
    def __init__(self, inputs, input_key='close', desc="Cross Sessional Scale"):
        super(Scale, self).__init__(inputs=inputs, np_func=lambda x: x/np.sum(np.abs(x)),
                                      name=PipeLine.get_name(Scale.__name__, inputs, input_key),
                                      input_key=input_key, length=1, desc=desc)


class DecayLinear(CrossSessionalApply):
    def __init__(self, inputs, length=20, input_key='close', desc="Cross Sessional DecayLinear"):
        super(DecayLinear, self).__init__(inputs=inputs,
                                          np_func=lambda x: np.dot(np.arange(length, 0, -1), x)
                                                            / np.sum(np.arange(length, 0, -1)),
                                      name=PipeLine.get_name(DecayLinear.__name__, inputs, input_key),
                                      input_key=input_key, length=length, desc=desc)


class DecayExp(CrossSessionalApply):
    def __init__(self, inputs, f=0.9, length=20, input_key='close', desc="Cross Sessional DecayExp"):
        super(DecayExp, self).__init__(inputs=inputs,
                                       np_func=lambda x: np.dot(np.power(f, np.arange(length)), x)/np.sum(np.power(f, np.arange(length))),
                                      name=PipeLine.get_name(DecayExp.__name__, inputs, input_key),
                                      input_key=input_key, length=length, desc=desc)


class TsRank(CrossSessionalApply):
    def __init__(self, inputs, ascending=True, length=20, input_key='close', desc="Cross Sessional Timeseries Rank"):
        super(TsRank, self).__init__(inputs=inputs, np_func=lambda x : timeseries_rank_helper(x,ascending=ascending),
                                      name=PipeLine.get_name(TsRank.__name__, inputs, input_key),
                                      input_key=input_key, length=length, desc=desc)


class SignPower(CrossSessionalApply):
    def __init__(self, inputs, input_key='close', desc="Cross Sessional SignPower"):
        super(SignPower, self).__init__(inputs=inputs, np_func=lambda x: np_sign_to_value(x)* np.power(x, e),
                                      name=PipeLine.get_name(SignPower.__name__, inputs, input_key),
                                      input_key=input_key, length=1, desc=desc)


class Delta(CrossSessionalApply):
    def __init__(self, inputs, length, input_key='close', desc="Cross Sessional Delta"):
        super(Delta, self).__init__(inputs=inputs, np_func=lambda x: x[-1,:] - x[0,:],
                                      name=PipeLine.get_name(Delta.__name__, inputs, input_key),
                                      input_key=input_key, length=length, desc=desc)


class Product(CrossSessionalApply):
    def __init__(self, inputs, length, input_key='close', desc="Cross Sessional Product"):
        super(Product, self).__init__(inputs=inputs, np_func=lambda x: np.prod(x,axis=0),
                                      name=PipeLine.get_name(Product.__name__, inputs, input_key),
                                      input_key=input_key, length=length, desc=desc)



from jinja2 import Template
csTemplate = Template(
"""
class {{className}}(CrossSessionalApply):
    def __init__(self, inputs, input_key='close', desc="Cross Sessional {{className}}"):
        super({{className}}, self).__init__(inputs=inputs, np_func={{func}},
                                      name=PipeLine.get_name({{className}}.__name__, inputs, input_key),
                                      input_key=input_key, length=1, desc=desc)
"""
)
# print csTemplate.render({"className": "Tail",
#                          "func" : "lambda  x: x[np.logical_and(x>lb, x<up)] = val"})
#
# print csTemplate.render({"className": "Sign",
#                          "func" : "lambda x: np_sign_to_value(x)"})
#
# print csTemplate.render({"className": "Log",
#                          "func" : "lambda x: np.log(x)"})
#
# print csTemplate.render({"className": "SignPower",
#                          "func" : "lambda x: np_sign_to_value(x)* np.power(x, e)"})
#
# print csTemplate.render({"className": "Scale",
#                          "func" : "lambda x: x/np.sum(np.abs(x))"})
#
# print csTemplate.render({"className": "DecayLinear",
#                          "func": "lambda x: np.dot(np.arange(n,0,-1), x)/np.sum(np.arange(n,0,-1))"})

# print csTemplate.render({"className": "DecayExp",
#                          "func": "lambda x: np.dot(np.power(f,np.arange(n)), x)/np.sum(np.power(f,np.arange(n)))"})
#
# print csTemplate.render({"className": "TsRank",
#                          "func": "lambda x : timeseries_rank_helper(x,ascending=asc)"
#                          })

# print csTemplate.render({"className": "Delta",
#                          "func" : "lambda x: x[-1,:] - x[0,:]"})
#
#
# print csTemplate.render({"className": "Product",
#                          "func" : "lambda x: np.prod(x,axis=0)"})
