from typing import Dict

from algotrader import Context
from algotrader.model.model_factory import ModelFactory
from algotrader.model.time_series_pb2 import TimeSeriesUpdateEvent
from algotrader.trading.data_series import DataSeries
from algotrader.utils.data_series import build_series_id
from algotrader.utils.model import get_full_cls_name


class Indicator(DataSeries):
    VALUE = 'value'

    @staticmethod
    def get_name(indicator_name, input, input_key, *args):
        if not input:
            return '%s' % indicator_name
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

    def __init__(self, time_series=None, inputs=None, input_keys = None, desc=None, **kwargs):
        if inputs and not isinstance(inputs, list):
            inputs = list(inputs)
        self.calculate = True
        self.input_series = []


        if not time_series:
            series_id = build_series_id(self.__class__.__name__, inputs, input_keys, **kwargs)
            time_series = ModelFactory.build_time_series(series_id=series_id,
                                                         series_cls=get_full_cls_name(self),
                                                         desc=desc,
                                                         inputs=inputs, input_keys=input_keys, **kwargs)

        super(Indicator, self).__init__(time_series=time_series)

        for input in inputs:
            if isinstance(input, DataSeries):
                self.input_series.append(input)

    def _start(self, app_context: Context) -> None:
        super(Indicator, self)._start(self.app_context)

        self.app_context.inst_data_mgr.add_series(self)

        if not self.input_series:
            if not hasattr(self.time_series, 'inputs') or not self.time_series.inputs:
                for input in self.time_series.inputs:
                    self.input_series.append(self.app_context.inst_data_mgr.get_series(input.source))

        self._update_from_inputs()
        self._subscribe_inputs()

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
                        self._process_update(source=input.source, timestamp=timestamp, data=filtered_data)
                    else:
                        self._process_update(source=input.source, timestamp=timestamp, data=data)

    def on_update(self, event: TimeSeriesUpdateEvent):
        self._process_update(event.source, event.item.timestamp, event.item.data)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        raise NotImplementedError()
