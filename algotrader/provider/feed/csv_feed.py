import pandas as pd

from algotrader.event import EventBus, Bar, BarSize, BarType
from algotrader.provider import Feed, feed_mgr
from algotrader.trading.ref_data import inmemory_ref_data_mgr

dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')


class CSVDataFeed(Feed):
    ID = "CSV"

    def __init__(self, path='../data', ref_data_mgr=None, data_event_bus=None):
        self.__path = path
        self.__ref_data_mgr = ref_data_mgr if ref_data_mgr else inmemory_ref_data_mgr
        self.__data_event_bus = data_event_bus if data_event_bus else EventBus.data_subject

        feed_mgr.register(self)

    def start(self):
        pass

    def stop(self):
        pass

    def id(self):
        return CSVDataFeed.ID

    @staticmethod
    def read_csv(symbol, file):
        df = pd.read_csv(file, index_col='Date', parse_dates=['Date'], date_parser=dateparse)
        df['Symbol'] = symbol
        df['BarSize'] = int(BarSize.D1)
        return df

    def subscribe_all_mktdata(self, sub_keys):
        self.__read_csv([sub_keys])

    def subscribe_mktdata(self, sub_key):
        self.__read_csv([sub_key])

    def __read_csv(self, sub_keys):

        self.dfs = []
        for sub_key in sub_keys:

            ## TODO support different format, e.g. BAR, Quote, Trade csv files
            if sub_key.data_type == Bar and sub_key.bar_type == BarType.Time and sub_key.bar_size == BarSize.D1:
                inst = self.__ref_data_mgr.get_inst(inst_id=sub_key.inst_id)
                symbol = inst.get_symbol(self.ID)
                df = self.read_csv(symbol, '%s/%s.csv' % (self.__path, symbol.lower()))
                self.dfs.append(df)

        self.df = pd.concat(self.dfs).sort_index(0, ascending=True)

        for index, row in self.df.iterrows():
            ## TODO support bar filtering // from date, to date
            inst = self.__ref_data_mgr.get_inst(symbol=row['Symbol'])
            self.__data_event_bus.on_next(
                Bar(inst_id=inst.inst_id,
                    timestamp=index,
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    vol=row['Volume'],
                    adj_close=row['Adj Close'],
                    size=row['BarSize']))

    def unsubscribe_mktdata(self, sub_key):
        pass
