
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.utils.time_series import TimeSeries


class Indicator(TimeSeries):
    _slots__ = (
        'input',
        'calculate',
    )

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

def get_or_create_indicator(cls_name, *args, **kwargs):
    name = globals()[cls_name].get_name(*args, **kwargs)
    if not inst_data_mgr.has_series(name):
        return globals()[cls_name](*args, **kwargs)
    return inst_data_mgr.get_series(name, create_if_missing=False)
