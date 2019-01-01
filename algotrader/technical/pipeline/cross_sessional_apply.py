import numpy as np
import pandas as pd
from typing import Dict

from algotrader.model.time_series_pb2 import TimeSeriesUpdateEvent
from algotrader.technical.pipeline import PipeLine


# TODO: One output scalar
# TODO: Output Vector Apply class

class CrossSessionalApply(PipeLine):
    def __init__(self, time_series=None, inputs=None, input_keys='close',
                 desc="Bundle and Sync DataSeries to Vector", np_func=None, length=30, **kwargs):
        super(CrossSessionalApply, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys,
                                                  desc=desc,
                                                  length=length, **kwargs)
        self.np_func = np_func

    def on_update(self, event: TimeSeriesUpdateEvent):
        super(CrossSessionalApply, self).on_update(event)
        self._process_update(event.source, event.item.timestamp, event.item.data)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.inputs[0].size() >= self.length:
            if self.all_filled():
                # result[PipeLine.VALUE] = self.np_func(self.df.values)
                packed_matrix = np.transpose(np.array(self.cache.values()))
                # TODO review this if this correctly handle higher dimension array stored in cache
                if len(packed_matrix.shape) == 3:
                    packed_matrix = packed_matrix[:, 0, :]
                # TODO what if the cache value is a higher dimension matrix?
                result[PipeLine.VALUE] = self.np_func(packed_matrix)
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


class CrossSessionalApplyScala(PipeLine):
    def __init__(self, time_series=None, inputs=None, input_keys='close',
                 desc="Cross Sessional Apply", np_func=None, length=30):
        super(CrossSessionalApplyScala, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys,
                                                       desc=desc,
                                                       length=length)
        self.np_func = np_func

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        super(CrossSessionalApplyScala, self)._process_update(source=source, timestamp=timestamp, data=data)
        result = {}
        if self.inputs[0].size() >= self.length:
            if self.all_filled():
                packed_matrix = np.transpose(np.array(self.cache.values()))
                # TODO review this if this correctly handle higher dimension array stored in cache
                if len(packed_matrix.shape) == 3:
                    packed_matrix = packed_matrix[:, 0, :]
                # TODO what if the cache value is a higher dimension matrix?
                result[PipeLine.VALUE] = self.np_func(packed_matrix)
                # result[PipeLine.VALUE] = self.np_func(self.df.values)
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
        return np.array([1, 1])


class Average(CrossSessionalApplyScala):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional Average"):
        super(Average, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                      np_func=np.average, length=1)


class Sum(CrossSessionalApplyScala):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional Sum"):
        super(Sum, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  np_func=np.sum, length=1)


# TODO: Add Count , Abs, Sum,

class Abs(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional Abs"):
        super(Abs, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  np_func=np.abs, length=1)


def np_assign_on_mask(x, lb, ub, newval):
    x[np.logical_and(x > lb, x < ub)] = newval
    return x


def np_sign_to_value(x):
    x[x > 0] = 1
    x[x < 0] = -1
    return x


def sign_power(x, e):
    return np_sign_to_value(x) * np.power(x, e)


def timeseries_rank_helper(x, ascending):
    df = pd.DataFrame(x)
    return ((df.rank(axis=0, ascending=ascending) - 1) / (df.shape[0] - 1)).tail(1).values


class Tail(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional Tail", lb=None, ub=None,
                 newval=None):
        super(Tail, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                   np_func=None, length=1, lb=lb, ub=ub, newval=newval)
        lb = self.get_float_config('lb', lb)
        ub = self.get_float_config('ub', ub)
        newval = self.get_float_config('newval', newval)
        self.np_func = lambda x: np_assign_on_mask(x, lb, ub, newval)


class Sign(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional Sign"):
        super(Sign, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                   np_func=lambda x: np_sign_to_value(x), length=1)


class Log(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional Log"):
        super(Log, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                  np_func=lambda x: np.log(x), length=1)


class Scale(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional Scale"):
        super(Scale, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                    np_func=lambda x: x / np.sum(np.abs(x)), length=1)


class DecayLinear(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional DecayLinear",length=20):
        super(DecayLinear, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                          np_func=lambda x: np.dot(np.arange(self.length, 0, -1), x)
                                                            / np.sum(np.arange(self.length, 0, -1)), length=length)


class DecayExp(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional DecayExp", f=0.9,
                 length=20):
        super(DecayExp, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                       np_func=None, f=f, length=length)

        f = self.get_float_config('f', f)
        self.np_func = lambda x: np.dot(np.power(f, np.arange(self.length)), x) / np.sum(
            np.power(f, np.arange(self.length)))


class TsRank(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional Timeseries Rank",
                 ascending=True,
                 length=20):
        super(TsRank, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                     np_func=None, length=length, ascending=ascending)

        ascending = self.get_bool_config('ascending', ascending)
        self.np_func = lambda x: timeseries_rank_helper(x, ascending=ascending)


class SignPower(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional SignPower", e=2):
        super(SignPower, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                        np_func=None, length=1, e=e)
        e = self.get_int_config("e", e)
        self.np_func = lambda x: np_sign_to_value(x) * np.power(x, e)


class Delta(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional Delta", length=1):
        super(Delta, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                    np_func=lambda x: np.prod(x, axis=0), length=length)


class Product(CrossSessionalApply):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Cross Sessional Product", length=1):
        super(Product, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                      np_func=lambda x: np.dot(np.arange(self.length, 0, -1), x)
                                                        / np.sum(np.arange(self.length, 0, -1)), length=length)


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
