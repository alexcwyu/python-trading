from algotrader.technical import Indicator


class DataSeriesUtils(object):
    def __init__(self, app_context):
        self.app_context = app_context
        pass

    def parse(self, name):
        if not self.app_context.inst_data_mgr.has_series(name):
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
                inner = self.parse(inner_str)
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
                inner = self.parse(inner_str)
                arg = [inner]
                arg += arg_str.split(',')
                return globals()[cls_str](*arg)
        return self.app_context.inst_data_mgr.get_series(name)

    def get_or_create_indicator(self, cls, *args, **kwargs):
        name = Indicator.get_name(cls, *args, **kwargs)
        if not self.app_context.inst_data_mgr.has_series(name):
            return globals()[cls](*args, **kwargs)
        return self.app_context.inst_data_mgr.get_series(name, create_if_missing=False)
