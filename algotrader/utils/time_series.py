from collections import defaultdict

import numpy as np
import pandas as pd
from rx.subjects import Subject
import datetime

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
        self.description = description if description else id
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
        'description',
        'data',
        'subject',
        '_value',
        '_prev_time',
        '_size',
        '_missing_value'
    )

    def __init__(self, name=None, description=None, missing_value=np.nan):
        self.name = name
        self.description = description if description else id
        self.data = defaultdict(dict)
        self.subject = Subject()
        self._value = defaultdict(list)
        self._prev_time = defaultdict(lambda: None)
        self._size = defaultdict(lambda: 0)
        self._missing_value = missing_value

    def add(self, time, values):
        assert type(values) == dict
        for key, value in values.items():
            if self._prev_time[key] == None or time > self._prev_time[key]:
                self.data[key][time] = value
                self._value[key].append(value)
                self._size[key] += 1
                self._prev_time[key] = time
            elif time == self._prev_time[key]:
                self.data[key][time] = value
                self._value[key].pop()
                self._value[key].append(value)
            else:
                raise AssertionError(
                    "Time for new Item %s cannot be earlier then previous item %s" % (time, self._prev_time))
        self.subject.on_next((time, values))

    def get_data(self, keys=None):
        return self.__get_result_for_keys(keys, lambda key: self.data[key])

    def get_series(self, keys=None):
        def f(key):
            s = pd.Series(self.data[key], name="%s.%s" % (self.name, key))
            s.index.name = 'Time'
            return s

        return self.__get_result_for_keys(keys, f)

    def size(self, keys=None):
        return self.__get_result_for_keys(keys, lambda key: self._size[key])

    def now(self, keys=None):
        return self.__get_result_for_keys(keys, lambda key: self.get_by_idx(key, -1))

    def get_by_idx(self, key, idx=None):
        if idx == None:
            return self._value[key]
        elif isinstance(idx, int) and (idx >= self._size[key] or idx < -self._size[key]):
            return self._missing_value
        return self._value[key][idx]

    def get_by_time(self, key, time):
        return self.data[key][time]

    def ago(self, keys=None, idx=1):
        assert idx >= 0
        return self.__get_result_for_keys(keys, lambda key: self.get_by_idx(key, -1 - idx))

    def std(self, keys=None, start=None, end=None):
        return self.__call_np(keys, start, end, np.nanstd)

    def var(self, keys=None, start=None, end=None):
        return self.__call_np(keys, start, end, np.nanvar)

    def mean(self, keys=None, start=None, end=None):
        return self.__call_np(keys, start, end, np.nanmean)

    def max(self, keys=None, start=None, end=None):
        return self.__call_np(keys, start, end, np.nanmax)

    def min(self, keys=None, start=None, end=None):
        return self.__call_np(keys, start, end, np.nanmin)

    def median(self, keys=None, start=None, end=None):
        return self.__call_np(keys, start, end, np.nanmedian)

    def __get_result_for_keys(self, keys, function):
        result = {}
        if not keys:
            keys = self.data.keys()
        if type(keys) != set and type(keys) != list:
            keys = [keys]
        for key in keys:
            result[key] = function(key)
        return result

    def __call_np(self, keys, start, end, np_func):

        def f(key):
            idx = self.__create_slice(key, start, end)
            data = self.get_by_idx(key, idx)
            return np_func(data)

        return self.__get_result_for_keys(keys, f)

    def __create_slice(self, key, start=None, end=None):
        if not end:
            end = self.size([key])[key]
        if start:
            return slice(start, end)
        else:
            return slice(end)

    def __getitem__(self, idx):
        key, index = idx
        if isinstance(index, slice) or isinstance(index, int):
            return self.get_by_idx(key, index)
        elif isinstance(index, datetime.datetime):
            return self.get_by_time(key, index)
        raise NotImplementedError("Unsupported index type %s, %s" % (index, type(index)))


def cross_above(value1, value2, look_up_period=1):
    pass


def cross_below(value1, value2, look_up_period=1):
    pass


def __cross_impl(value1, value2, func, start=-2, end=-1):
    pass

