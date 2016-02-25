from algotrader.provider import *
from algotrader.event.market_data import *
from algotrader.trading.order_mgr import *
import pandas as pd


class CSVDataFeed(Provider):
    pass


dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')


class PandasCSVDataFeed(CSVDataFeed):
    def __init__(self, names, subject=None):
        if not subject:
            subject = EventBus.data_subject
        self.subject = subject
        self.dfs = []
        for name in names:
            df = pd.read_csv('../../data/%s.csv' % name, index_col='Date', parse_dates=['Date'], date_parser=dateparse)
            df['Symbol'] = name
            df['Frequency'] = 24 * 60 * 60
            self.dfs.append(df)

        self.df = pd.concat(self.dfs).sort_index(0, ascending=True)

    def start(self):
        for index, row in self.df.iterrows():
            self.subject.on_next(
                    Bar(instrument=row['Symbol'], timestamp=index, open=row['Open'], high=row['High'], low=row['Low'], close=row['Close'], vol=row['Volume'],
                        adj_close=row['Adj Close'], freq=row['Frequency']))

    def stop(self):
        pass
