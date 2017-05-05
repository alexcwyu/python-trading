from algotrader.technical import Indicator


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
    name = Indicator.get_name(cls, *args, **kwargs)
    if not inst_data_mgr.has_series(name):
        return globals()[cls](*args, **kwargs)
    return inst_data_mgr.get_series(name, create_if_missing=False)
