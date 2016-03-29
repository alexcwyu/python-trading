import numpy as np
import pandas as pd
from rx.subjects import Subject


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
        self.__size = 0

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
            raise AssertionError("Time for new Item %s cannot be earlier then previous item %s" % (time, self.__prev_time))
        self.subject.on_next((time, value))

    def get_data(self):
        return self.data

    def get_series(self):
        s = pd.Series(self.data, name=self.id)
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
            return np.nan
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

    values = [np.nan, np.nan, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
              45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]

    for idx, value in enumerate(values):
        close.add(t, value)
        t = t + datetime.timedelta(0, 3)
        print close.now(), close.ago(0), close.ago(1), close.ago(2)

    print close[0:2]
    print close[0:4]
    print close[0:8]

    print "mean"
    print close.mean()
    print close.mean(0, 4)
    print close.mean(0, 6)

    print "median"
    print close.median()
    print close.median(0, 4)
    print close.median(0, 6)

    print "max"
    print close.max()
    print close.max(0, 4)
    print close.max(0, 6)

    print "min"
    print close.min()
    print close.min(0, 4)
    print close.min(0, 6)

    print "std"
    print close.std()
    print close.std(0, 4)
    print close.std(0, 6)

    print "var"
    print close.var()
    print close.var(0, 4)
    print close.var(0, 6)
