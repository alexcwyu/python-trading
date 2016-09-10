import pandas as pd

from algotrader.config.feed import CSVFeedConfig
from algotrader.event.market_data import Bar, BarSize, BarType
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.utils.date_utils import DateUtils

dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')


class CSVDataFeed(Feed):
    def __init__(self, app_context=None):
        super(CSVDataFeed, self).__init__()
        self.csv_config = app_context.app_config.get_config(CSVFeedConfig)
        self.path = self.csv_config.path

    def _start(self, app_context=None):
        self.ref_data_mgr = self.app_context.ref_data_mgr
        self.data_event_bus = self.app_context.event_bus.data_subject

    def _stop(self):
        pass

    def id(self):
        return Feed.CSV

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
            if isinstance(sub_key.subscription_type,
                          BarSubscriptionType) and sub_key.subscription_type.bar_type == BarType.Time and sub_key.subscription_type.bar_size == BarSize.D1:
                inst = self.ref_data_mgr.get_inst(inst_id=sub_key.inst_id)
                symbol = inst.get_symbol(self.ID)
                df = self.read_csv(symbol, '%s/%s.csv' % (self.path, symbol.lower()))
                self.dfs.append(df)

        self.df = pd.concat(self.dfs).sort_index(0, ascending=True)

        for index, row in self.df.iterrows():
            ## TODO support bar filtering // from date, to date
            inst = self.ref_data_mgr.get_inst(symbol=row['Symbol'])
            self.data_event_bus.on_next(
                Bar(inst_id=inst.inst_id,
                    timestamp=DateUtils.datetime_to_unixtimemillis(index),
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    vol=row['Volume'],
                    adj_close=row['Adj Close'],
                    size=row['BarSize']))

    def unsubscribe_mktdata(self, sub_key):
        pass
