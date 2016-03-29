# from collections import OrderedDict
from rx.subjects import Subject

import pandas as pd
import numpy as np
import datetime


class TimeSeries(object):
    _slots__ = (
        'id',
        'description',
        'data',
        'subject',
        '__key',
        '__prev_time',
        '__size'
    )

    def __init__(self, id=None, description=None):
        self.id = id
        self.description = description if description else id
        self.data = dict()
        self.subject = Subject()
        self.__value = list()
        self.__prev_time = None
        # self.__last_value = np.nan
        # self.__prev_value = np.nan
        self.__size = 0

    def add(self, time, value):
        if time in self.data:
            raise RuntimeError("time %s already in data" % time)
        self.data[time] = value
        self.__value.append(value)
        self.subject.on_next((time, value))
        # self.__prev_value = self.__last_value
        # self.__last_value = value
        self.__size += 1

    def get_data(self):
        return self.data

    def get_series(self):
        s = pd.Series(self.data, name=self.id)
        s.index.name = 'Time'
        return s

    def size(self):
        return self.__size

    def now(self):
        # return self.value[-1] if self.lenght>0 else 0
        # return self.__value[-1] if len(self.__value) > 0 else np.nan
        return self.get_by_idx(-1)

    def get_by_idx(self, idx=None):
        # if idx == -1 or idx == self.__size - 1:
        #     return self.__last_value
        # elif idx == -2 or idx == self.__size - 2:
        #     return self.__prev_value
        if not idx:
            return self.__value
        elif isinstance(idx, int) and (idx >= self.__size or idx < -self.__size):
            return np.nan
        return self.__value[idx]

    def get_by_time(self, time):
        return self.data[time]

    def ago(self, idx=1):
        assert idx >= 0
        return self.get_by_idx(-1 - idx)

    def std(self, idx=None):
        data = self.get_by_idx(idx)
        return np.nanstd(data)

    def var(self, idx=None):
        data = self.get_by_idx(idx)
        return np.nanvar(data)

    def mean(self, idx=None):
        data = self.get_by_idx(idx)
        return np.nanmean(data)

    def max(self, idx = None):
        data = self.get_by_idx(idx)
        return np.nanmax(data)

    def min(self, idx = None):
        data = self.get_by_idx(idx)
        return np.nanmin(data)

    def median(self, idx = None):
        data = self.get_by_idx(idx)
        return np.nanmedian(data)

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


if __name__ == "__main__":
    import datetime

    close = TimeSeries("close")

    t = datetime.datetime.now()

    values = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
              45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]

    for idx, value in enumerate(values):
        close.add(t, value)
        t = t + datetime.timedelta(0, 3)
        print close.now(), close.ago(0), close.ago(1),close.ago(2)


    print close[0:2]
    print close[0:4]
    print close[0:8]

    print close.mean()
    print close.mean(slice(0,2))
    print close.mean(slice(0,4))
    print close.mean(slice(0,8))