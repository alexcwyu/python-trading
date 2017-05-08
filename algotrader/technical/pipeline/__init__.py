import numpy as np
from collections import OrderedDict

from algotrader.model.model_factory import ModelFactory
from algotrader.technical import Indicator
from algotrader.trading.data_series import DataSeries, DataSeriesEvent
from algotrader import Context

class PipeLine(DataSeries):
    VALUE = 'value'
    _slots__ = (
        'inputs',
        'numPipes',
        'length',
        'input_keys',
        'cache'
        'input_names_pos',
        'input_keys',
        '__curr_timestamp'
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
            # parts.extend(Indicator.get_input_name(inputs))
            parts.append(Indicator.get_input_name(inputs))

        return ",".join(str(part) for part in parts)

    def __init__(self, name, inputs, input_keys, length=None, desc=None, time_series=None, *args, **kwargs):

        # super(PipeLine, self).__init__(name=name, keys=None, desc=desc, *args, **kwargs)

        # f = lambda i: i \
        #     if isinstance(i, DataSeries) or isinstance(i, Indicator) \
        #     else inst_data_mgr.get_series(i)
        # if isinstance(inputs, list):
        #     self.inputs = [f(i) for i in inputs]
        # else:
        #     self.inputs = f(inputs)

        input_names = []
        self.input_names_and_series = OrderedDict()
        if isinstance(inputs, list):
            for i in inputs:
                if isinstance(i, DataSeries):
                    input_name = DataSeries.get_name(i)
                    input_names.append(input_name)
                    self.input_names_and_series[input_name] = i
                elif isinstance(i, Indicator):
                    input_name = Indicator.get_name(i)
                    input_names.append(input_name)
                    self.input_names_and_series[input_name] = i
                elif isinstance(i, PipeLine):
                    input_name = PipeLine.get_name(i)
                    input_names.append(input_name)
                    self.input_names_and_series[input_name] = i
                else:
                    input_names.append(i)
        else:
            if isinstance(inputs, DataSeries):
                input_name = DataSeries.get_name(inputs)
                input_names.append(input_name)
                self.input_names_and_series[input_name] = inputs
            elif isinstance(inputs, Indicator):
                input_name = Indicator.get_name(inputs)
                input_names.append(input_name)
                self.input_names_and_series[input_name] = inputs
            elif isinstance(inputs, PipeLine):
                input_name = PipeLine.get_name(inputs)
                input_names.append(input_name)
                self.input_names_and_series[input_name] = inputs
            else:
                input_names.append(inputs)

        self.numPipes = len(input_names)
        self.length = length if length is not None else 1
        self.input_names = input_names
        self.input_names_pos = dict(zip(input_names,
                                        range(len(input_names))))

        self.input_keys = self._get_key(input_keys, None)
        # self.calculate = True
        self.__curr_timestamp = None
        self._flush_and_create()
        self.inputs = []

        super(PipeLine, self).__init__(
            ModelFactory.build_time_series(series_id=name, name=name, desc=desc, inputs=self.input_names))

        # self.df = pd.DataFrame(index=range(self.length), columns=input_names)
        # self.cache = {} # key is input name, value is numpy array
        # self.update_all()

    def _start(self, app_context: Context) -> None:
        super(PipeLine, self)._start(self.app_context)

        # if not hasattr(self, 'inputs') or not self.inputs:
        #     self.inputs = [self.app_context.inst_data_mgr.get_series(name) for name in self.input_names]
        missing_input_names = [k for k, v in self.input_names_and_series.items() if v is None]
        for name in missing_input_names:
            self.input_names_and_series[name] = self.app_context.inst_data_mgr.get_series(name)

        self.inputs = [v for k, v in self.input_names_and_series.items()]
        self.app_context.inst_data_mgr.add_series(self)

        self.update_all()
        # for i in self.inputs:
        for i in self.inputs:
            i.subject.subscribe(self.on_update)

    def _stop(self):
        pass

    def _flush_and_create(self):
        # self.df = pd.DataFrame(index=range(self.length), columns=self.input_names)
        self.cache = OrderedDict(zip(self.input_names, [None for i in range(len(self.input_names))]))

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
        """
        PipeLine specify function, check in all input in self.inputs have been updated
        :return:
        """
        has_none = np.sum(np.array([v is None for v in self.cache.values()]))
        return False if has_none > 0 else True
        # check_df = self.df.isnull()*1
        # return False if check_df.sum(axis=1).sum(axis=0) > 0 else True

    def on_update(self, event: DataSeriesEvent):
        data = event.data
        timestamp = event.timestamp
        data_name = event.name
        if timestamp != self.__curr_timestamp:
            self.__curr_timestamp = timestamp
            self._flush_and_create()

        if data_name in self.input_names:
            j = self.input_names_pos[data_name]
            self.cache[data_name] = self.inputs[j].get_by_idx(
                keys=self.input_keys,
                idx=slice(-self.length, None, None))
            # self.df[data_name] = self.inputs[j].get_by_idx(
            #     keys=self.input_keys,
            #     idx=slice(-self.length, None, None))

    def numPipes(self):
        return self.numPipes

    def shape(self):
        raise NotImplementedError()
