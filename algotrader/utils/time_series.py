from collections import defaultdict

import numpy as np
import pandas as pd
from rx.subjects import Subject
import datetime

timestamp_key = "timestamp"

class TimeSeries(object):
    _slots__ = (
        'name',
        'description',
        'data',
        'subject',
        '__value',
        '__prev_time',
        '__size',
        '__missing_value'
    )

    def __init__(self, name=None, description=None, missing_value=np.nan):
        self.name = name
        self.description = description if description else name
        self.data = dict()
        self.subject = Subject()
        self.__value = list()
        self.__prev_time = None
        self.__size = 0
        self.__missing_value = missing_value

    def add(self, time, value):
        if self.__prev_time == None or time > self.__prev_time:
            self.data[time] = value
            self.__value.append(value)
            self.__size += 1
            self.__prev_time = time
        elif time == self.__prev_time:
            self.data[time] = value
            self.__value.pop()
            self.__value.append(value)
        else:
            raise AssertionError(
                "Time for new Item %s cannot be earlier then previous item %s" % (time, self.__prev_time))
        self.subject.on_next((time, value))

    def get_data(self):
        return self.data

    def get_series(self):
        s = pd.Series(self.data, name=self.name)
        s.index.name = 'Time'
        return s

    def size(self):
        return self.__size

    def now(self):
        return self.get_by_idx(-1)

    def get_by_idx(self, idx=None):
        if idx == None:
            return self.__value
        elif isinstance(idx, int) and (idx >= self.__size or idx < -self.__size):
            return self.__missing_value
        return self.__value[idx]

    def get_by_time(self, time):
        return self.data[time]

    def ago(self, idx=1):
        assert idx >= 0
        return self.get_by_idx(-1 - idx)

    def std(self, start=None, end=None):
        idx = self.__create_slice(start, end)
        data = self.get_by_idx(idx)
        return np.nanstd(data)

    def var(self, start=None, end=None):
        idx = self.__create_slice(start, end)
        data = self.get_by_idx(idx)
        return np.nanvar(data)

    def mean(self, start=None, end=None):
        idx = self.__create_slice(start, end)
        data = self.get_by_idx(idx)
        return np.nanmean(data)

    def max(self, start=None, end=None):
        idx = self.__create_slice(start, end)
        data = self.get_by_idx(idx)
        return np.nanmax(data)

    def min(self, start=None, end=None):
        idx = self.__create_slice(start, end)
        data = self.get_by_idx(idx)
        return np.nanmin(data)

    def median(self, start=None, end=None):
        idx = self.__create_slice(start, end)
        data = self.get_by_idx(idx)
        return np.nanmedian(data)

    def __create_slice(self, start=None, end=None):
        if not end:
            end = self.size()
        if start:
            return slice(start, end)
        else:
            return slice(end)

    def __getitem__(self, index):
        if isinstance(index, slice) or isinstance(index, int):
            return self.get_by_idx(index)
        elif isinstance(index, datetime.datetime):
            return self.get_by_time(index)
        raise NotImplementedError("Unsupported index type %s, %s" % (index, type(index)))


class DataSeries(object):
    _slots__ = (
        'name',
        'keys',
        'default_key',
        'desc',
        'missing_value'
        'subject',

        '__time_data_dict',
        '__data_dict',
        '__prev_time',
        '__size',
    )

    def __init__(self, name=None, keys=None, default_key=None, desc=None, missing_value=np.nan, data_list=None):
        self.name = name
        self.keys = keys
        self.default_key = default_key
        self.desc = desc if desc else name
        self.missing_value = missing_value
        self.subject = Subject()

        self.__data_list = defaultdict(list)
        self.__time_list = list()
        self.__data_time_dict = defaultdict(dict)

        if data_list:
            for data in data_list:
                self.add(data)

    def add(self, data):
        time = data.get(timestamp_key)
        if not self.keys:
            self.keys = data.keys()
        if self.current_time() == None or time > self.current_time():
            self.__time_list.append(time)
            for key in self.keys :
                value = data.get(key, self.missing_value)
                self.__data_time_dict[key][time] = value
                self.__data_list[key].append(value)

        elif time == self.current_time():
            for key in self.keys:
                if key in data:
                    value = data.get(key)
                    self.__data_list[key].pop()
                    self.__data_list[key].append(value)
                    self.__data_time_dict[key][time] = value
        else:
            raise AssertionError(
                "Time for new Item %s cannot be earlier then previous item %s" % (time, self._prev_time))
        self.subject.on_next(data)


    def current_time(self):
        return  self.__time_list[-1] if self.__time_list else None

    def get_data(self, keys=None):
        keys = self._get_key(keys)
        result = {}
        for key in keys:
            result[key] = self.__data_time_dict[key]
        return result if len(keys) > 1 else result[keys[0]]


    def get_data_frame(self, keys=None):
        df = pd.DataFrame(self.__data_list, index=self.__time_list)
        if keys:
            return df[self._get_key(keys)]
        return df


    def get_series(self, keys):
        df = self.get_data_frame(keys)
        keys = self._get_key(keys)
        result = {}
        for key in keys:
            result[key] = df[key]
        return result if len(keys) > 1 else result[keys[0]]


    def size(self):
        return len(self.__time_list)

    def now(self, keys=None):
        return self.get_by_idx(-1, keys)

    def _get_key(self, keys= None):
        keys = keys if keys else self.keys
        if type(keys) != set and type(keys) != list:
            keys = [keys]
        return keys


    def get_by_idx(self, idx, keys=None):
        if (isinstance(idx, int) and (idx >= self.size() or idx < -self.size())) or idx == None:
            return self.missing_value
        keys = self._get_key(keys)
        result = {}
        for key in keys:
            result[key] = self.__data_list[key][idx]

        return result if len(keys) > 1 else result[keys[0]]

    def get_by_time(self, time, keys=None):
        keys = self._get_key(keys)
        result = {}
        for key in keys:
            result[key] = self.__data_time_dict[key][time]

        return result if len(keys) > 1 else result[keys[0]]


    def ago(self, idx=1, keys = None):
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

    # def __get_result_for_keys(self, keys, function):
    #     result = {}
    #     keys = self._get_key(keys)
    #     for key in keys:
    #         result[key] = function(key)
    #     return result

    def __call_np(self, keys, start, end, np_func):

        def f(idx, key):
            data = self.get_by_idx(idx, key)
            return np_func(data)

        idx = self.__create_slice(start, end)

        result = {}
        keys = self._get_key(keys)
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

