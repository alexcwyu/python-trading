import datetime

import numpy as np
import pandas as pd
from rx.subjects import Subject
# from algotrader.technical.pipeline.pairwise import Plus, Minus, Times, Divides

from algotrader import Startable
from algotrader.provider.persistence import Persistable

timestamp_key = "timestamp"


class DataSeries(Persistable, Startable):
    TIMESTAMP = 'timestamp'

    __slots__ = (
        'name',
        'keys',
        'desc',
        'missing_value',
        'data_list',
        'time_list',
        'data_time_dict',
        'use_col_np'
    )

    __transient__ = (
        'subject',
        'app_context',
    )

    @staticmethod
    def get_name(input):
        if isinstance(input, DataSeries):
            return "'%s'" % input.name
        return "'%s'" % input

    def __init__(self, name=None, keys=None, desc=None, missing_value=np.nan, data_list=None, use_col_np=False):
        """
        :param name:
        :param keys:
        :param desc:
        :param missing_value:
        :param data_list:
        :param use_col_np: If True, the column based storage of list will used to pass to numpy function
        """
        super(DataSeries, self).__init__()
        self.name = name
        self.keys = self._get_key(keys, None)
        self.desc = desc if desc else name
        self.missing_value = missing_value

        self.data_list = []
        self.time_list = []
        self.data_time_dict = {}
        self.use_col_np = use_col_np

        self.subject = Subject()

        if data_list:
            for data in data_list:
                self.add(data)

    def _start(self, app_context, **kwargs):
        pass

    def _stop(self):
        pass

    def id(self):
        return self.name

    def add(self, data):
        data["name"] = DataSeries.get_name(self)
        time = data.get(timestamp_key)
        if not self.keys:
            self.keys = data.keys()

        if self.current_time() == None or time > self.current_time():
            self.time_list.append(time)
            enhanced_data = {}
            for key in self.keys:
                value = data.get(key, self.missing_value)
                if key not in self.data_time_dict:
                    self.data_time_dict[key] = {}
                self.data_time_dict[key][str(time)] = value
                enhanced_data[key] = value
            self.data_list.append(enhanced_data)

        elif time == self.current_time():

            enhanced_data = self.data_list.pop()
            for key in self.keys:
                if key in data:
                    value = data.get(key)
                    if key not in self.data_time_dict:
                        self.data_time_dict[key] = {}
                    self.data_time_dict[key][str(time)] = value
                    enhanced_data[key] = value
            self.data_list.append(enhanced_data)
        else:
            raise AssertionError(
                "Time for new Item %s cannot be earlier then previous item %s" % (time, self.current_time()))
        self.subject.on_next(data)

    def current_time(self):
        return self.time_list[-1] if self.time_list else None

    def get_data_dict(self, keys=None):
        keys = self._get_key(keys, self.keys)
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
            return df[self._get_key(keys, self.keys)]
        return df

    def get_series(self, keys):
        df = self.get_data_frame(keys)
        keys = self._get_key(keys, self.keys)
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
            return self.missing_value
        keys = self._get_key(keys, self.keys)
        result = {}
        for key in keys:
            if isinstance(idx, int):
                result[key] = self.data_list[idx].get(key, self.missing_value)
            elif isinstance(idx, slice):
                result[key] = [data.get(key, self.missing_value) for data in self.data_list[idx]]
            else:
                raise AssertionError("unknown index type %s" % (idx))

        return result if len(keys) > 1 else result[keys[0]]

    def get_by_time(self, time, keys=None):
        keys = self._get_key(keys, self.keys)
        result = {}
        for key in keys:
            if key in self.data_time_dict:
                result[key] = self.data_time_dict[key][str(time)]

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
        keys = self._get_key(keys, self.keys)
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
        keys = self._get_key(keys, self.keys)
        for key in keys:
            data = self.get_by_idx(idx, key)
            result[key] = func(np.array(data), *argv, **kwargs)
        return result if len(keys) > 1 else result[keys[0]]
    #
    # def __add__(self, other):
    #     return Plus(self, other, self.keys)
    #
    # def __radd__(self, other):
    #     return Plus(other, self, self.keys)
    #
    # def __mul__(self, other):
    #     return Times(self, other, self.keys)
    #
    # def __rmul__(self, other):
    #     return Times(other, self, self.keys)


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
