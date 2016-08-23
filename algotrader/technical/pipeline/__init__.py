from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.utils.time_series import DataSeries
from algotrader.technical import Indicator
import numpy as np

class PipeLine(Indicator):
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
        parts.extend(PipeLine.get_input_name(inputs))

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

    def __init__(self, name, inputs, input_keys, desc=None):
        super(PipeLine, self).__init__(name=name, desc=desc)
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
        self.input_names_pos = dict(zip(input_names,
                                        range(len(input_names))))

        self.input_keys = self._get_key(input_keys, None)
        self.input.subject.subscribe(self.on_update)
        inst_data_mgr.add_series(self)
        self.calculate = True
        # self.current_slice = np.empty(len(self.input_keys))
        self.current_slice = None
        # self.update_all()

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



