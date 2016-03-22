import pandas as pd
from collections import OrderedDict

class TimeSeries():
    # time = Value(np.empty([0], dtype='datetime64'))
    # value = Value(np.empty([0], dtype='float'))
    # lenght = Int(0)

    def __init__(self):
        self.__data = OrderedDict()

    def add(self, time, value):
        self.__data[time] = value

    def get_data(self):
        return self.__data

    def get_series(self):
        # return pd.Series(data=self.value, index=self.time)
        s = pd.Series(self.__data, name='Value')
        s.index.name = 'Time'
        return s

    def size(self):
        return len(self.__data)

    def current_value(self):
        # return self.value[-1] if self.lenght>0 else 0
        return self.__data.items()[-1][1] if len(self.__data) > 0 else 0

    def get_value_by_idx(self, idx):
        return self.__data.items()[idx][1]

    def get_value_by_time(self, time):
        return self.__data[time]
