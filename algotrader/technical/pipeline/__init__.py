import numpy as np
from collections import OrderedDict
from typing import Dict, List

from algotrader import Context
from algotrader.technical import Indicator


class PipeLine(Indicator):
    def __init__(self, time_series=None, inputs=None, input_keys=None, desc=None,
                 keys: List[str] = None, default_output_key: str = 'value', **kwargs):

        super(PipeLine, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                       keys=keys, default_output_key=default_output_key, **kwargs)

        self.length = self.get_int_config("length", 1)
        self.__curr_timestamp = None

    def _start(self, app_context: Context) -> None:
        super(PipeLine, self)._start(self.app_context)
        self.numPipes = len(self.input_series)
        self._flush_and_create()

    def _stop(self):
        pass

    def _flush_and_create(self):
        self.cache = OrderedDict(zip(list(self.input_names_pos.keys()), [None for _ in range(len(self.input_series))]))

    def all_filled(self):
        """
        PipeLine specify function, check in all input in self.inputs have been updated
        :return:
        """
        has_none = np.sum(np.array([v is None for v in self.cache.values()]))
        return False if has_none > 0 else True

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        if timestamp != self.__curr_timestamp:
            self.__curr_timestamp = timestamp
            self._flush_and_create()

        if source in self.input_names_pos:
            idx = self.input_names_pos[source]
            self.cache[source] = self.get_input(idx).get_by_idx(
                keys=self.get_input_keys(idx=idx),
                idx=slice(-self.length, None, None))

    def numPipes(self):
        return self.numPipes

    def shape(self):
        raise NotImplementedError()
