
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.utils.time_series import TimeSeries


class Indicator(TimeSeries):
    _slots__ = (
        'input',
        'calculate',
    )

    @staticmethod
    def get_input_name(input):
        if isinstance(input, Indicator):
            return input.name
        if isinstance(input, TimeSeries):
            return "'%s'"%input.name
        return "'%s'"%input

    def __init__(self, name, input, description):
        super(Indicator, self).__init__(name, description)
        if isinstance(input, TimeSeries):
            self.input = input
        else:
            self.input = inst_data_mgr.get_series(input)
        self.input.subject.subscribe(self.on_update)
        inst_data_mgr.add_series(self)
        self.calculate = True
        self.update_all()

    def update_all(self):
        data = self.input.get_data()
        keylist = data.keys()
        keylist.sort()
        for time in keylist:
            self.on_update(time, data[time])

    def on_update(self, time_value):
        raise NotImplementedError()

from algotrader.technical.atr import ATR
from algotrader.technical.bb import BB
from algotrader.technical.ma import SMA
from algotrader.technical.roc import ROC
from algotrader.technical.rsi import RSI
from algotrader.technical.stats import MAX
from algotrader.technical.stats import MIN
from algotrader.technical.stats import STD
from algotrader.technical.stats import VAR

def parse(name):
    if not inst_data_mgr.has_series(name):
        count = name.count("(")
        if count >1 :
            lidx = name.find("(")
            ridx = name.rfind(")", 0, -1)
            assert name.endswith(")") , "invalid syntax, cannot parse %s" % name
            assert lidx > -1 , "invalid syntax, cannot parse %s" % name
            assert ridx > lidx , "invalid syntax, cannot parse %s" % name

            cls_str =  name[0:lidx]
            inner_str = name[lidx+1 : ridx+1]
            arg_str = name[ridx + 2:-1]
            inner = parse(inner_str)
            arg = [inner]
            arg += arg_str.split(',')
            return globals()[cls_str](*arg)
        elif count == 1 :
            lidx = name.find("(")
            ridx = name.find(",")
            assert name.endswith(")") , "invalid syntax, cannot parse %s" % name
            assert lidx > -1 , "invalid syntax, cannot parse %s" % name
            assert ridx > lidx , "invalid syntax, cannot parse %s" % name

            cls_str = name[0:lidx]
            inner_str = name[lidx+1: ridx].strip(' \'\"')
            arg_str = name[ridx + 1:-1]
            inner = parse(inner_str)
            arg = [inner]
            arg += arg_str.split(',')
            return globals()[cls_str](*arg)
    return inst_data_mgr.get_series(name)



def get_or_create_indicator(cls, *args, **kwargs):
    name = globals()[cls].get_name(*args, **kwargs)
    if not inst_data_mgr.has_series(name):
        return globals()[cls](*args, **kwargs)
    return inst_data_mgr.get_series(name, create_if_missing=False)

#
#
# def get_or_create_indicator_by_str(name):
#     if not inst_data_mgr.has_series(name):
#         return globals()[cls](*args, **kwargs)
#     return inst_data_mgr.get_series(name, create_if_missing=False)