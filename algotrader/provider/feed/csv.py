import abc

import pandas as pd

from algotrader.event import EventBus, Bar, BarSize
from algotrader.provider import Feed

dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')


class CSVDataFeed(Feed):
    __metaclass__ = abc.ABCMeta


class PandasCSVDataFeed(CSVDataFeed):
    def __init__(self, names, subject=None):
        if not subject:
            subject = EventBus.data_subject
        self.subject = subject
        self.dfs = []
        for name in names:
            df = self.read_csv(name, '../../data/%s.csv' % name)
            self.dfs.append(df)

        self.df = pd.concat(self.dfs).sort_index(0, ascending=True)

    def start(self):
        for index, row in self.df.iterrows():
            self.subject.on_next(
                Bar(instrument=row['Symbol'], timestamp=index, open=row['Open'], high=row['High'], low=row['Low'],
                    close=row['Close'], vol=row['Volume'],
                    adj_close=row['Adj Close'], size=row['BarSize']))

    def stop(self):
        pass

    def id(self):
        return "PandasCSV"

    @staticmethod
    def read_csv(symobl, file):
        df = pd.read_csv(file, index_col='Date', parse_dates=['Date'], date_parser=dateparse)
        df['Symbol'] = symobl
        df['BarSize'] = int(BarSize.D1)
        return df
