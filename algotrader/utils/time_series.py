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


class MultiTimeSeries(object):
    _slots__ = (
        'name',
        'keys',
        'default_key',
        'description',
        'series_dict',
        'subject',
        '__value',
        '__prev_time',
        '__size',
        '__missing_value'
    )

    def __init__(self, name, keys, default_key, description=None, missing_value=np.nan):
        self.name = name
        self.keys= keys
        self.default_key = default_key
        self.description = description if description else name
        self.series_dict = dict()
        self.subject = Subject()
        if keys is not None:
            for key in keys:
                self.series_dict[key] = TimeSeries(name="%s.%s" % (name, key), missing_value=missing_value)
        self.__value = list()
        self.__prev_time = None
        self.__size = 0
        self.__missing_value = missing_value

    def get_key(self, key=None):
        if not key:
            return self.default_key

    def add(self, time, data):
        for key, value in data:
            self.series_dict[key].add(time, value)
        self.subject.on_next((time, data))

    def get_data(self, key=None):
        return self.series_dict[self.get_key(key)].get_data()

    def get_series(self, key=None):
        s = pd.Series(self.get_data(key), name=self.name)
        s.index.name = 'Time'
        return s


    def size(self, key=None):
        return self.series_dict[self.get_key(key)].size()

    def now(self, key=None):
        return self.get_by_idx(-1)

    def get_by_idx(self, key=None, idx=None):
        return self.series_dict[self.get_key(key)].get_by_idx(idx)

    def get_by_time(self, key=None, time=None):
        return self.series_dict[self.get_key(key)].get_by_time(time)


    def ago(self, key=None, idx=1):
        return self.series_dict[self.get_key(key)].ago(idx)

    def std(self, key=None, start=None, end=None):
        return self.series_dict[self.get_key(key)].std(start, end)

    def var(self, key=None, start=None, end=None):
        return self.series_dict[self.get_key(key)].var(start, end)

    def mean(self, key=None, start=None, end=None):
        return self.series_dict[self.get_key(key)].mean(start, end)

    def max(self, key=None, start=None, end=None):
        return self.series_dict[self.get_key(key)].max(start, end)

    def min(self, key=None, start=None, end=None):
        return self.series_dict[self.get_key(key)].min(start, end)

    def median(self, key=None, start=None, end=None):
        return self.series_dict[self.get_key(key)].median(start, end)

    def __getitem__(self, key):
        return self.series_dict[self.get_key(key)]


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

    def __init__(self, name, keys, default_key, desc=None, missing_value=np.nan):
        self.name = name
        self.keys = keys
        self.default_key = default_key
        self.desc = desc if desc else name
        self.missing_value = missing_value
        self.subject = Subject()

        self.__data_list = defaultdict(list)
        self.__time_list = list()
        self.__data_time_dict = defaultdict(dict)

    def add(self, time, data):
        if self.current_time() == None or time > self.current_time():
            for key in self.keys:
                value = data.get(key, default=self.missing_value)
                self.__data_time_dict[key][time] = value
                self.__data_list[key].append(value)
                self.__time_list.append(time)

        elif time == self.current_time():
            for key in self.keys:
                value = data.get(key, default=self.missing_value)
                self.__data_list[key].pop()
                self.__data_list[key].append(value)
        else:
            raise AssertionError(
                "Time for new Item %s cannot be earlier then previous item %s" % (time, self._prev_time))
        self.subject.on_next((time, data))


    def current_time(self):
        return  self.__time_list[-1] if self.__time_list else None

    def get_data(self, keys=None):
        if not keys:
            self.__data_time_dict
        else:
            result = {}
            for key in keys:
                result[key] = self.__data_time_dict[key]

    def get_series(self, keys=None):
        df = pd.DataFrame(self.__data_list, index=self.__time_list)
        if keys:
            return df[self._get_key(keys)]
        return df


    def size(self):
        return len(self.__time_list)

    def now(self, keys=None):
        return self.get_by_idx(keys, -1)

    def _get_key(keys= None):
        keys = keys if keys else self.keys
        if type(keys) != set and type(keys) != list:
            keys = [keys]
        return keys


    def get_by_idx(self, idx=None, keys=None):
        if isinstance(idx, int) and (idx >= self.size() or idx < -self.size()):
            return self.__missing_value
        keys = self._get_key(keys)
        result = {}
        for key in keys:
            result[key] = self.__data_list[key][idx] if idx else self.__data_list[key]

        return result

    def get_by_time(self, time, keys=None):
        keys = self._get_key(keys)
        result = {}
        for key in keys:
            result[key] = self.__data_time_dict[key][time]
        return result


    def ago(self, idx=1, keys = None):
        assert idx >= 0
        return self.get_by_idx(-1 - idx)


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
        return result


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


def cross_above(value1, value2, look_up_period=1):
    pass


def cross_below(value1, value2, look_up_period=1):
    pass


def __cross_impl(value1, value2, func, start=-2, end=-1):
    pass

