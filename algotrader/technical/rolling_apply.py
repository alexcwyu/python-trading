import numpy as np
from algotrader.technical.function_wrapper import *

def rolling_window(arr, periods):
    shape = arr.shape[:-1] + (arr.shape[-1] - periods + 1, periods)
    strides = arr.strides + (arr.strides[-1],)
    return np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)


def highest_function(arr):
    if arr.ndim == 1:
        return np.max(arr)
    else:
        return np.max(arr, axis=1)

def lowest_function(arr):
    if arr.ndim == 1:
        return np.min(arr)
    else:
        return np.min(arr, axis=1)


def highest(arr, periods):
    result_arr = np.empty_like(arr)
    result_arr[:] = np.NAN
    result_arr[periods-1:] = highest_function(rolling_window(arr, periods))
    return result_arr


def lowest(arr, periods):
    result_arr = np.empty_like(arr)
    result_arr[:] = np.NAN
    result_arr[periods-1:] = lowest_function(rolling_window(arr, periods))
    return result_arr


highest30 = periods_function(periods=30, name='highest30')(highest) # 30 period hightest
lowest30 = periods_function(periods=30, name='lowest30')(lowest) # 30 period hightest

# import numpy as np
# import pandas as pd
# from typing import Dict
#
# from algotrader.technical import Indicator
#
#
# class RollingApply(Indicator):
#     _slots__ = (
#         'length',
#         'func'
#     )
#
#     def __init__(self, time_series=None, inputs=None, input_keys=None, desc="Rolling Apply", length=0, func=np.std):
#         super(RollingApply, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
#                                            length=length)
#         self.func = func
#         self.length = self.get_int_config("length", 0)
#
#     def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
#         result = {}
#         if self.first_input.size() >= self.length:
#             sliced = self.first_input.get_by_idx(keys=self.first_input_keys, idx=slice(-self.length, None, None))
#             result[Indicator.VALUE] = self.func(sliced)
#         else:
#             result[Indicator.VALUE] = np.nan
#
#         self.add(timestamp=timestamp, data=result)
# #
# class StdDev(RollingApply):
# def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Rolling Standard Deviation", length=30):
#     super(StdDev, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
#                                  length=length, func=lambda x: np.std(x, axis=0))
#
#
# def pd_skew_wrapper(x):
# ts = pd.Series(x)
# return ts.skew()
#
#
# def pd_kurtosis_wrapper(x):
# ts = pd.Series(x)
# return ts.kurtosis()
#
#
# def pd_kurt_wrapper(x):
# ts = pd.Series(x)
# return ts.kurt()
#
#
# class Skew(RollingApply):
# def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Rolling Skew", length=30):
#     super(Skew, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
#                                length=length, func=lambda x: pd_skew_wrapper(x))
#
#
# class Kurtosis(RollingApply):
# def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Rolling Kurtosis", length=30):
#     super(Kurtosis, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
#                                    length=length, func=lambda x: pd_kurtosis_wrapper(x))
#
#
# class Kurt(RollingApply):
# def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Rolling Kurt", length=30):
#     super(Kurt, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
#                                length=length, func=lambda x: pd_kurt_wrapper(x))
#
# #
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
