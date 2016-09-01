from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.utils.time_series import DataSeries
from algotrader.technical import Indicator
import numpy as np
import pandas as pd


class PipeLine(DataSeries):
    VALUE = 'value'
    _slots__ = (
        'input',
        'input_keys',
        'calculate',
        'input_names_pos'
    )

    @staticmethod
    def get_name(indicator_name, inputs, input_key, *args):
        parts = []
        parts.extend(DataSeries.convert_to_list(PipeLine.get_input_name(inputs)))

        if input_key:
            parts.extend(DataSeries.convert_to_list(input_key))
        if args:
            parts.extend(args)
        content = ",".join(str(part) for part in parts)
        return '%s(%s)' % (indicator_name, content)

    @staticmethod
    def get_input_name(inputs):
        parts = []
        if isinstance(inputs, list):
            parts.extend([Indicator.get_input_name(i) for i in inputs])
        else:
            parts.extend(Indicator.get_input_name(inputs))

        return ",".join(str(part) for part in parts)

    def __init__(self, name, inputs, input_keys, length=None, desc=None):
        super(PipeLine, self).__init__(name=name, keys=input_keys, desc=desc)
        f = lambda i: i \
            if isinstance(i, DataSeries) or isinstance(i, Indicator) \
            else inst_data_mgr.get_series(i)
        if isinstance(inputs, list):
            self.inputs = [f(i) for i in inputs]
        else:
            self.inputs = f(inputs)

        input_names = []
        for i in inputs:
            if isinstance(i, DataSeries):
                input_names.append(DataSeries.get_name(i))
            elif isinstance(i, Indicator):
                input_names.append(Indicator.get_name(i))
            else:
                input_names.append(i)

        self.length = length if length is not None else 1
        self.input_names = input_names
        self.df = pd.DataFrame(index=range(self.length), columns=input_names)
        self.input_names_pos = dict(zip(input_names,
                                        range(len(input_names))))

        self.input_keys = self._get_key(input_keys, None)
        [input.subject.subscribe(self.on_update) for input in self.inputs]
        inst_data_mgr.add_series(self)
        self.calculate = True
        self.__curr_timestamp = None
        # self.update_all()

    def _flush_and_create(self):
        self.df = pd.DataFrame(index=range(self.length), columns=self.input_names)


    def update_all(self):
        for input in self.inputs:
            data_list = input.get_data()
            for data in data_list:
                if self.input_keys:
                    filtered_data = {key: data[key] for key in self.input_keys}
                    filtered_data['timestamp'] = data['timestamp']
                    self.on_update(filtered_data)
                else:
                    self.on_update(data)

    def all_filled(self):
        check_df = self.df.isnull()*1
        return False if check_df.sum(axis=1).sum(axis=0) > 0 else True

    def on_update(self, data):
        if data['timestamp'] != self.__curr_timestamp:
            self.__curr_timestamp = data['timestamp']
            self._flush_and_create()

        data_name = data['name']
        if data_name in self.input_names:
            j = self.input_names_pos[data_name]
            self.df[data_name] = self.inputs[j].get_by_idx(
                keys=self.input_keys,
                idx=slice(-self.length, None, None))






