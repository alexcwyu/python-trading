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
        '__key'
    )

    def __init__(self, id=None, description=None):
        self.id = id
        self.description = description if description else id
        self.data = dict()
        self.subject = Subject()
        self.__key = list()

    def add(self, time, value):
        if time not in self.data:
            self.__key.append(time)
        self.data[time] = value
        self.subject.on_next((time, value))

    def get_data(self):
        return self.data

    def get_series(self):
        s = pd.Series(self.data, name=self.id)
        s.index.name = 'Time'
        return s

    def size(self):
        return len(self.data)

    def now(self):
        # return self.value[-1] if self.lenght>0 else 0
        return self.data[self.__key[-1]] if len(self.__key) > 0 else np.nan

    def get_by_idx(self, idx):
        return self.data[self.__key[idx]]

    def get_by_time(self, time):
        return self.data[time]

    def ago(self, idx=1):
        assert idx >= 0
        return self.get_by_idx(-1 - idx)

    def __getitem__(self, index):
        if isinstance(index, int):
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
