import pandas as pd
from tzlocal import get_localzone


def parse_series(inst_data_mgr, name):
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


def get_or_create_indicator(inst_data_mgr, cls, *args, **kwargs):
    # name = get_name(cls, *args, **kwargs)
    name = None
    if not inst_data_mgr.has_series(name):
        return globals()[cls](*args, **kwargs)
    return inst_data_mgr.get_series(name, create_if_missing=False)


def convert_series_idx_to_datetime(series: pd.Series) -> pd.Series:
    return pd.Series(series.values,
                     index=pd.to_datetime(series.index, unit='ms').tz_localize('UTC')
                     .tz_convert(get_localzone().zone))


def get_input_name(input):
    if hasattr(input, 'time_series') and input.time_series:
        return "%s" % input.time_series.series_id
    return "%s" % input  # str


def build_series_id(name: str, inputs=None, input_keys=None, **kwargs):
    parts = []
    if inputs:
        if not isinstance(inputs, list):
            inputs = [inputs]

        input_keys = input_keys if input_keys else {}
        for input in inputs:
            input_name = get_input_name(input)
            if isinstance(input_keys, dict):
                if input_name in input_keys:
                    keys = input_keys[input_name]

                    if isinstance(keys, str):
                        parts.append('%s[%s]' % (input_name, keys))
                    else:
                        parts.append('%s[%s]' % (input_name, ','.join(keys)))
                else:
                    parts.append(input_name)
            elif isinstance(input_keys, str):
                parts.append('%s[%s]' % (input_name, input_keys))
            else:
                parts.append('%s[%s]' % (input_name, ','.join(input_keys)))

    if kwargs:
        for key, value in kwargs.items():
            parts.append('%s=%s' % (key, value))

    if parts:
        return "%s(%s)" % (name, ','.join(parts))
    else:

        return "%s()" % name


def build_indicator(cls, name, input, input_keys, desc=None, time_series=None):
    pass
