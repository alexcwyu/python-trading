from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.utils.time_series import DataSeries


class Indicator(DataSeries):
    VALUE = 'value'
    __slots__ = (
        'input_name',
        'input_keys',
        'calculate',
    )

    @staticmethod
    def get_name(indicator_name, input, input_key, *args):
        parts = [Indicator.get_input_name(input)]
        if input_key:
            parts.extend(DataSeries.convert_to_list(input_key))
        if args:
            parts.extend(args)
        content = ",".join(str(part) for part in parts)
        return '%s(%s)' % (indicator_name, content)

    @staticmethod
    def get_input_name(input):
        if isinstance(input, Indicator):
            return input.name
        if isinstance(input, DataSeries):
            return "'%s'" % input.name
        return "'%s'" % input

    def __init__(self, name, input, input_keys, desc=None, **kwargs):
        super(Indicator, self).__init__(name=name, desc=desc, **kwargs)

        self.input_keys = self._get_key(input_keys, None)
        inst_data_mgr.add_series(self)
        self.calculate = True

        if input:
            if isinstance(input, DataSeries):
                self.input_name = input.name
                self.input = input
            else:
                self.input_name = input
                self.input = inst_data_mgr.get_series(input)

            self.input.subject.subscribe(self.on_update)
            self.update_all()

    def update_all(self):
        data_list = self.input.get_data()
        for data in data_list:
            if self.input_keys:
                filtered_data = {key: data[key] for key in self.input_keys}
                filtered_data['timestamp'] = data['timestamp']
                self.on_update(filtered_data)
            else:
                self.on_update(data)

    def on_update(self, data):
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
        if count > 1:
            lidx = name.find("(")
            ridx = name.rfind(")", 0, -1)
            assert name.endswith(")"), "invalid syntax, cannot parse %s" % name
            assert lidx > -1, "invalid syntax, cannot parse %s" % name
            assert ridx > lidx, "invalid syntax, cannot parse %s" % name

            cls_str = name[0:lidx]
            inner_str = name[lidx + 1: ridx + 1]
            arg_str = name[ridx + 2:-1]
            inner = parse(inner_str)
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
            inner = parse(inner_str)
            arg = [inner]
            arg += arg_str.split(',')
            return globals()[cls_str](*arg)
    return inst_data_mgr.get_series(name)


def get_or_create_indicator(cls, *args, **kwargs):
    name = Indicator.get_name(cls, *args, **kwargs)
    if not inst_data_mgr.has_series(name):
        return globals()[cls](*args, **kwargs)
    return inst_data_mgr.get_series(name, create_if_missing=False)

    #
    #
    # def get_or_create_indicator_by_str(name):
    #     if not inst_data_mgr.has_series(name):
    #         return globals()[cls](*args, **kwargs)
    #     return inst_data_mgr.get_series(name, create_if_missing=False)
