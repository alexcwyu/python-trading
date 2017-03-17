import datetime
from typing import Dict

import numpy as np
import pandas as pd
from rx.subjects import Subject

from algotrader import Startable
from algotrader.model.model_helper import ModelHelper
from algotrader.model.time_series_pb2 import TimeSeries


class DataSeriesEvent(object):
    def __init__(self, name: str, timestamp: int, data: Dict[str, float]):
        self.name = name
        self.timestamp = timestamp
        self.data = data


class DataSeries(Startable):
    TIMESTAMP = 'timestamp'

    @staticmethod
    def get_name(input):
        if isinstance(input, DataSeries):
            return "'%s'" % input.time_series.series_id
        return "'%s'" % input

    def __init__(self, time_series: TimeSeries):
        self.time_series = time_series
        self.name = time_series.name
        self.data_list = []
        self.time_list = []
        self.data_time_dict = {}
        self.subject = Subject()

        if time_series and time_series.items:
            for item in time_series.items:
                self.add(dict(item.data), item.timestamp, True)

    def _start(self, app_context, **kwargs):
        pass

    def _stop(self):
        pass

    def id(self):
        return self.time_series.name

    def add(self, data: Dict[str, float], timestamp: int = None, init: bool = False) -> None:
        timestamp = timestamp if timestamp is not None else data.get(DataSeries.TIMESTAMP)

        if not self.time_series.keys:
            ModelHelper.add_to_list(self.time_series.keys, data.keys())

        if not self.time_series.start_time:
            self.time_series.start_time = timestamp

        enhanced_data = {}
        if not self.time_series.end_time \
                or timestamp > self.time_series.end_time \
                or len(self.data_list) == 0:

            self.time_list.append(timestamp)

            for key in list(self.time_series.keys):
                value = data.get(key, self.time_series.missing_value_replace)
                if key not in self.data_time_dict:
                    self.data_time_dict[key] = {}
                self.data_time_dict[key][timestamp] = value
                enhanced_data[key] = value

            # self.data_list.append(enhanced_data)
            if not init:
                self.last_item = self.time_series.items.add()
                ModelHelper.add_to_dict(self.last_item.data, enhanced_data)

        elif timestamp == self.time_series.end_time:

            enhanced_data = self.data_list.pop()
            for key in list(self.time_series.keys):
                if key in data:
                    value = data.get(key)
                    if key not in self.data_time_dict:
                        self.data_time_dict[key] = {}
                    self.data_time_dict[key][timestamp] = value
                    enhanced_data[key] = value
            if not init:
                ModelHelper.add_to_dict(self.last_item.data, enhanced_data)
        else:
            raise AssertionError(
                "Time for new Item %s cannot be earlier then previous item %s" % (timestamp, self.current_time()))

        self.time_series.end_time = timestamp
        self.data_list.append(enhanced_data)
        self.subject.on_next(DataSeriesEvent(name=DataSeries.get_name(self), timestamp=timestamp, data=data))

    def current_time(self):
        return self.time_series.end_time

    def get_data_dict(self, keys=None):
        keys = self._get_key(keys, list(self.time_series.keys))
        result = {}
        for key in keys:
            if key in self.data_time_dict:
                result[key] = self.data_time_dict[key]
        return result if len(keys) > 1 else result[keys[0]]

    def get_data(self):
        return self.data_list

    def get_data_frame(self, keys=None):
        df = pd.DataFrame(self.data_list, index=self.time_list)
        if keys:
            return df[self._get_key(keys, list(self.time_series.keys))]
        return df

    def get_series(self, keys):
        df = self.get_data_frame(keys)
        keys = self._get_key(keys, list(self.time_series.keys))
        result = {}
        for key in keys:
            result[key] = df[key]
        return result if len(keys) > 1 else result[keys[0]]

    def size(self):
        return len(self.time_list)

    def now(self, keys=None):
        return self.get_by_idx(-1, keys)

    def _get_key(self, keys=None, default_keys=None):
        keys = keys if keys else default_keys
        return DataSeries.convert_to_list(keys)

    @staticmethod
    def convert_to_list(items=None):
        if items and type(items) != set and type(items) != list:
            items = [items]
        return items

    def get_by_idx(self, idx, keys=None):
        if (isinstance(idx, int) and (idx >= self.size() or idx < -self.size())) or idx == None:
            return self.time_series.missing_value_replace
        keys = self._get_key(keys, list(self.time_series.keys))
        result = {}
        for key in keys:
            if isinstance(idx, int):
                result[key] = self.data_list[idx].get(key, self.time_series.missing_value_replace)
            elif isinstance(idx, slice):
                result[key] = [data.get(key, self.time_series.missing_value_replace) for data in self.data_list[idx]]
            else:
                raise AssertionError("unknown index type %s" % (idx))

        return result if len(keys) > 1 else result[keys[0]]

    def get_by_time(self, time, keys=None):
        keys = self._get_key(keys, list(self.time_series.keys))
        result = {}
        for key in keys:
            if key in self.data_time_dict:
                result[key] = self.data_time_dict[key][time]

        return result if len(keys) > 1 else result[keys[0]]

    def ago(self, idx=1, keys=None):
        assert idx >= 0
        return self.get_by_idx(-1 - idx, keys)

    def std(self, start=None, end=None, keys=None):
        return self.__call_np(keys, start, end, np.nanstd)

    def var(self, start=None, end=None, keys=None):
        return self.__call_np(keys, start, end, np.nanvar)

    def mean(self, start=None, end=None, keys=None):
        return self.__call_np(keys, start, end, np.nanmean)

    def max(self, start=None, end=None, keys=None):
        return self.__call_np(keys, start, end, np.nanmax)

    def min(self, start=None, end=None, keys=None):
        return self.__call_np(keys, start, end, np.nanmin)

    def median(self, start=None, end=None, keys=None):
        return self.__call_np(keys, start, end, np.nanmedian)

    def __call_np(self, keys, start, end, np_func):

        def f(idx, key):
            data = self.get_by_idx(idx, key)
            return np_func(data)

        idx = self.__create_slice(start, end)

        result = {}
        keys = self._get_key(keys, list(self.time_series.keys))
        for key in keys:
            result[key] = f(idx, key)
        return result if len(keys) > 1 else result[keys[0]]

    def __create_slice(self, start=None, end=None):
        if not end:
            end = self.size()
        if start:
            return slice(start, end)
        else:
            return slice(end)

    def apply(self, keys, start, end, func, *argv, **kwargs):
        """
        :param keys:
        :param start:
        :param end:
        :param func: numpy vectorized function that call apply on numpy array
        :param argv:
        :param kwargs:
        :return:
        """
        idx = self.__create_slice(start, end)

        result = {}
        keys = self._get_key(keys, list(self.time_series.keys))
        for key in keys:
            data = self.get_by_idx(idx, key)
            result[key] = func(np.array(data), *argv, **kwargs)
        return result if len(keys) > 1 else result[keys[0]]

    def __getitem__(self, pos):
        if isinstance(pos, tuple):
            index, keys = pos
        else:
            index, keys = (pos, None)
        if isinstance(index, slice) or isinstance(index, int):
            return self.get_by_idx(index, keys)
        elif isinstance(index, datetime.datetime):
            return self.get_by_time(index, keys)
        raise NotImplementedError("Unsupported index type %s, %s" % (index, type(index)))

    def cross_above(value1, value2, look_up_period=1):
        pass

    def cross_below(value1, value2, look_up_period=1):
        pass

    def __cross_impl(value1, value2, func, start=-2, end=-1):
        pass
