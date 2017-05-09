import re

from algotrader.utils.data_series import build_series_id
from algotrader.utils.model import get_cls


def parse_inner(inner_str, level):
    print(level, inner_str)
    inputs = []
    input_keys = {}
    kwargs = {}
    while "(" in inner_str:
        lidx = inner_str.find("(")
        ridx = inner_str.rfind(")")
        assert lidx > -1
        assert ridx > -1
        nested = inner_str[0:ridx]

        inner_str = inner_str[ridx+1:]


    for inner in inner_str.split(','):
        if '=' in inner:
            idx = inner.find("=")
            k = inner[0:idx]
            v = inner[idx + 1:]
            kwargs[k] = v
        elif '[' in inner:
            assert inner.endswith("]")
            idx = inner.find("[")
            input = inner[0:idx]
            keys = re.split('; |, ', inner[idx + 1: -1])
            inputs.append(input)
            input_keys[input] = keys
        else:
            inputs.append(inner)

    return inputs, input_keys, kwargs


def parse_series(inst_data_mgr, name):
    if not inst_data_mgr.has_series(name):
        lidx = name.find("(")
        assert name.endswith(")"), "invalid syntax, cannot parse %s" % name
        assert lidx > -1, "invalid syntax, cannot parse %s" % name
        cls_str = name[0:lidx]
        inner_str = name[lidx + 1:-1]

        inputs, input_keys, kwargs = parse_inner(inner_str)
        cls = globals()[cls_str]
        return cls(inputs=inputs, input_keys=input_keys, **kwargs)

    return inst_data_mgr.get_series(name)


def get_or_create_indicator(inst_data_mgr, cls, inputs=None, input_keys=None, **kwargs):
    cls = get_cls(cls)
    name = build_series_id(cls.__name__, inputs=inputs, input_keys=input_keys, **kwargs)
    if not inst_data_mgr.has_series(name):
        obj =  cls(inputs=inputs, input_keys=input_keys, **kwargs)
        inst_data_mgr.add_series(obj)
        return obj
    return inst_data_mgr.get_series(name, create_if_missing=False)
