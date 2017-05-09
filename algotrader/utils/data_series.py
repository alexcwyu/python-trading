import re

import pandas as pd
from typing import Dict, List
from tzlocal import get_localzone

from algotrader.utils.model import get_cls


def convert_series_idx_to_datetime(series: pd.Series) -> pd.Series:
    return pd.Series(series.values,
                     index=pd.to_datetime(series.index, unit='ms').tz_localize('UTC')
                     .tz_convert(get_localzone().zone))


def get_input_name(input):
    if hasattr(input, 'time_series') and input.time_series:
        return "%s" % input.time_series.series_id
    elif isinstance(input, str):
        return "%s" % input  # str
    raise Exception("only str or DataSeries is supported")


def convert_input_keys(inputs=None, input_keys=None) -> Dict[str, List[str]]:
    result = {}
    if inputs:
        input_keys = input_keys if input_keys else {}
        if isinstance(input_keys, dict):
            for k, v in input_keys.items():
                if isinstance(v, list):
                    result[k] = v
                elif isinstance(v, str):
                    result[k] = [v]

        if isinstance(input_keys, list):
            for input in inputs:
                input_name = get_input_name(input)
                result[input_name] = input_keys

        if isinstance(input_keys, str):
            for input in inputs:
                input_name = get_input_name(input)
                result[input_name] = [input_keys]

    return result


def build_series_id(name: str, inputs=None, input_keys=None, **kwargs):
    parts = []
    if inputs:
        if not isinstance(inputs, list):
            inputs = [inputs]
        input_keys = convert_input_keys(inputs, input_keys)
        for input in inputs:
            input_name = get_input_name(input)
            if input_name in input_keys:
                keys = input_keys[input_name]
                parts.append('%s[%s]' % (input_name, ','.join(keys)))
            else:
                parts.append(input_name)

    if kwargs:
        for key, value in kwargs.items():
            parts.append('%s=%s' % (key, value))

    if parts:
        return "%s(%s)" % (name, ','.join(parts))
    else:

        return "%s()" % name  #


# def build_indicator(cls, inputs=None, input_keys=None, desc=None, time_series=None, **kwargs):
#     if isinstance(cls, str):
#         if cls in cls_cache:
#             cls = cls_cache[cls]
#         else:
#             cls_name = cls
#             cls = dynamic_import(cls_name)
#             cls_cache[cls_name] = cls
#
#     if not time_series:
#         if inputs and not isinstance(inputs, list):
#             inputs = list(inputs)
#         series_id = build_series_id(cls.__name__, inputs, input_keys, **kwargs)
#         time_series = ModelFactory.build_time_series(series_id=series_id,
#                                                      series_cls=get_full_cls_name(cls),
#                                                      desc=desc,
#                                                      inputs=inputs, input_keys=input_keys, **kwargs)
#
#     return cls(time_series=time_series)


def convert_to_list(items=None):
    if items and type(items) != set and type(items) != list:
        items = [items]
    return items
