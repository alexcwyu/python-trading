from collections import OrderedDict
from rx.subjects import Subject

import pandas as pd


class TimeSeries(object):
    _slots__ = (
        'id',
        'description',
        'data',
        'subject',
    )

    def __init__(self, id=None, description=None):
        self.id = id
        self.description = description if description else id
        self.data = OrderedDict()
        self.subject = Subject()

    def add(self, time, value):
        self.data[time] = value
        self.subject.on_next((time, value))

    def get_data(self):
        return self.data

    def get_series(self):
        s = pd.Series(self.data, name='Value')
        s.index.name = 'Time'
        return s

    def size(self):
        return len(self.data)

    def current_value(self):
        # return self.value[-1] if self.lenght>0 else 0
        return self.data.items()[-1][1] if len(self.data) > 0 else 0

    def get_value_by_idx(self, idx):
        return self.data.items()[idx][1]

    def get_value_by_time(self, time):
        return self.data[time]
