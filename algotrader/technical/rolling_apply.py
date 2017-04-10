import numpy as np
import pandas as pd

from algotrader.technical import Indicator


class RollingApply(Indicator):
    _slots__ = (
        'length',
        'func'
    )

    def __init__(self, input, name, input_key=None, length=0, func=np.std, desc="Rolling Apply", *args, **kwargs):
        self.length = int(length)
        self.func = func
        super(RollingApply, self).__init__(name=name, input=input, input_keys=input_key, desc=desc, *args, **kwargs)

    def on_update(self, data):
        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            sliced = self.input.get_by_idx(keys=self.input_keys, idx=slice(-self.length, None, None))
            result[Indicator.VALUE] = self.func(sliced)
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)


class StdDev(RollingApply):
    def __init__(self, input, input_key='close', length=30, desc="Rolling Standard Deviation"):
        super(StdDev, self).__init__(input,
                                     func=lambda x: np.std(x, axis=0),
                                     name=Indicator.get_name(StdDev.__name__, input, input_key, length),
                                     length=length,
                                     input_key=input_key, desc=desc)


def pd_skew_wrapper(x):
    ts = pd.Series(x)
    return ts.skew()


def pd_kurtosis_wrapper(x):
    ts = pd.Series(x)
    return ts.kurtosis()


def pd_kurt_wrapper(x):
    ts = pd.Series(x)
    return ts.kurt()


class Skew(RollingApply):
    def __init__(self, input, input_key='close', length=30, desc="Rolling Skew"):
        super(Skew, self).__init__(input,
                                   func=lambda x: pd_skew_wrapper(x),
                                   name=Indicator.get_name(Skew.__name__, input, input_key, length),
                                   length=length,
                                   input_key=input_key, desc=desc)


class Kurtosis(RollingApply):
    def __init__(self, input, input_key='close', length=30, desc="Rolling Kurtosis"):
        super(Kurtosis, self).__init__(input,
                                       func=lambda x: pd_kurtosis_wrapper(x),
                                       name=Indicator.get_name(Kurtosis.__name__, input, input_key, length),
                                       length=length,
                                       input_key=input_key, desc=desc)


class Kurt(RollingApply):
    def __init__(self, input, input_key='close', length=30, desc="Rolling Kurt"):
        super(Kurt, self).__init__(input,
                                   func=lambda x: pd_kurt_wrapper(x),
                                   name=Indicator.get_name(Kurt.__name__, input, input_key, length),
                                   length=length,
                                   input_key=input_key, desc=desc)

#
#
# from jinja2 import Template
# rollingTmp = Template("""
# class {{className}}(RollingApply):
#     def __init__(self, input, input_key='close', length=30, desc="Rolling {{className}}"):
#         super({{className}}, self).__init__(input,
#                                      func={{func}},
#                                      name=Indicator.get_name({{className}}.__name__, input, input_key, length),
#                                      length=length,
#                                      input_key=input_key, desc=desc)
# """)
#
# print rollingTmp.render({"className": "Skew",
#                          "func" : "lambda x: pd_skew_wrapper(x)"})
#
# print rollingTmp.render({"className": "Kurtosis",
#                          "func" : "lambda x: pd_kurtosis_wrapper(x)"})
#
# print rollingTmp.render({"className": "Kurt",
#                          "func" : "lambda x: pd_kurt_wrapper(x)"})
