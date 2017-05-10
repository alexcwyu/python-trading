from typing import Dict, List

from algotrader import Context
from algotrader.model.model_factory import ModelFactory
from algotrader.model.time_series_pb2 import TimeSeriesUpdateEvent
from algotrader.trading.data_series import DataSeries
from algotrader.utils.data_series import build_series_id
from algotrader.utils.model import get_full_cls_name


class Indicator(DataSeries):
    VALUE = 'value'

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc=None,
                 keys: List[str] = None,
                 default_output_key: str = 'value', **kwargs):
        if not time_series:
            series_id = build_series_id(self.__class__.__name__, inputs, input_keys, **kwargs)
            time_series = ModelFactory.build_time_series(series_id=series_id,
                                                         series_cls=get_full_cls_name(self),
                                                         desc=desc,
                                                         inputs=inputs, input_keys=input_keys,
                                                         keys=keys,
                                                         default_output_key=default_output_key,
                                                         **kwargs)

        super(Indicator, self).__init__(time_series=time_series)

        self.calculate = True

        self.__raw_inputs = []

        if inputs:
            if not isinstance(inputs, list):
                self.__raw_inputs = [inputs]
            else:
                self.__raw_inputs = inputs

    def _init_inputs(self):

        self.input_keys = {}
        for time_series_input in self.time_series.inputs:
            if hasattr(time_series_input, 'keys') and time_series_input.keys:
                self.input_keys[time_series_input.source] = list(time_series_input.keys)

        self.input_series = []
        for __raw_input in self.__raw_inputs:
            if isinstance(__raw_input, DataSeries):
                self.input_series.append(__raw_input)
            elif isinstance(__raw_input, str):
                self.input_series.append(self.app_context.inst_data_mgr.get_series(__raw_input))

        self._update_from_inputs()
        self._subscribe_inputs()

        self.first_input = self.get_input(idx=0)
        self.first_input_keys = self.get_input_keys(idx=0)

    def get_input(self, idx: int) -> str:
        return self.input_series[idx]

    def get_input_keys(self, source=None, idx=None):
        source = source if source else self.get_input(idx).name
        return self.input_keys.get(source, None)

    def _start(self, app_context: Context) -> None:
        super(Indicator, self)._start(self.app_context)

        self.app_context.inst_data_mgr.add_series(self)

        self._init_inputs()

    def _stop(self):
        pass

    def _subscribe_inputs(self):
        for input in self.input_series:
            input.subject.subscribe(self.on_update)

    def _update_from_inputs(self):
        for input in self.input_series:
            for timestamp, data in zip(input.get_timestamp(), input.get_data()):
                # TODO handle multiple input_series....
                # if timestamp has been processed, we should skipped the update.....
                if timestamp not in self.time_list:
                    # TODO don't think we should put this filter logic here, the logic should be move to `_process_update`
                    if hasattr(input, 'keys') and input.keys:
                        filtered_data = {key: data[key] for key in input.keys}
                        self._process_update(source=input.id(), timestamp=timestamp, data=filtered_data)
                    else:
                        self._process_update(source=input.id(), timestamp=timestamp, data=data)

    def on_update(self, event: TimeSeriesUpdateEvent):
        self._process_update(event.source, event.item.timestamp, event.item.data)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        raise NotImplementedError()
