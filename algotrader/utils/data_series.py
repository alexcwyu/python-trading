import pandas as pd
from typing import Dict, List
from tzlocal import get_localzone
from algotrader.utils.model import get_cls



def parse_series(inst_data_mgr, name):
    from algotrader.technical import Indicator
    from algotrader.technical.ma import SMA
    from algotrader.technical.atr import ATR
    from algotrader.technical.bb import BB
    from algotrader.technical.ma import SMA
    from algotrader.technical.roc import ROC
    from algotrader.technical.rsi import RSI
    from algotrader.technical.stats import MAX
    from algotrader.technical.stats import MIN
    from algotrader.technical.stats import STD
    from algotrader.technical.stats import VAR
    if not inst_data_mgr.has_series(name):
        count = name.count("(")
        if count > 1:
            lidx = name.find("(")
            ridx = name.rfind(")", 0, -1)
            assert name.endswith(")"), "invalid syntax, cannot parse %s" % name
            assert lidx > -1, "invalid syntax, cannot parse %s" % name
            assert ridx > lidx, "invalid syntax, cannot parse %s" % name

            cls_str = name[0:lidx]
            inner_str = name[lidx + 1: ridx + 1]
            arg_str = name[ridx + 2:-1]
            inner = parse_series(inst_data_mgr, inner_str)
            arg = [inner]
            arg += arg_str.split(',')
            return globals()[cls_str](*arg)
        elif count == 1:
            lidx = name.find("(")
            ridx = name.find(",")
            assert name.endswith(")"), "invalid syntax, cannot parse %s" % name
            assert lidx > -1, "invalid syntax, cannot parse %s" % name
            assert ridx > lidx, "invalid syntax, cannot parse %s" % name

            cls_str = name[0:lidx]
            inner_str = name[lidx + 1: ridx].strip(' \'\"')
            arg_str = name[ridx + 1:-1]
            inner = parse_series(inst_data_mgr, inner_str)
            arg = [inner]
            arg += arg_str.split(',')
            return globals()[cls_str](*arg)
    return inst_data_mgr.get_series(name)


def get_or_create_indicator(inst_data_mgr, cls, inputs=None, input_keys=None, **kwargs):
    cls = get_cls(cls)
    name = build_series_id(cls.__name__, inputs=inputs, input_keys=input_keys,**kwargs)
    if not inst_data_mgr.has_series(name):
        return cls(inputs=inputs, input_keys=input_keys, **kwargs)
    return inst_data_mgr.get_series(name, create_if_missing=False)


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
                if isinstance(input_keys, list):
                    result[k] = v
                elif isinstance(input_keys, str):
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
