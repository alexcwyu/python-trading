import pandas as pd

from algotrader.config.feed import CSVFeedConfig
from algotrader.model.market_data_pb2 import Bar
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.utils.date_utils import DateUtils
from algotrader.utils.market_data_utils import BarSize

dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')

class CSVDataFeed(Feed):
    def __init__(self):
        super(CSVDataFeed, self).__init__()

    def _start(self, app_context, **kwargs):
        self.csv_config = app_context.app_config.get_config(CSVFeedConfig)
        self.path = self.csv_config.path
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

    def subscribe_mktdata(self, *sub_keys):
        self.__read_csv(*sub_keys)

    def __read_csv(self, *sub_keys):

        dfs = []
        sub_key_range = {sub_key.inst_id: (
            DateUtils.date_to_unixtimemillis(sub_key.from_date), DateUtils.date_to_unixtimemillis(sub_key.to_date)) for
                         sub_key in sub_keys}

        for sub_key in sub_keys:

            ## TODO support different format, e.g. BAR, Quote, Trade csv files
            if isinstance(sub_key.subscription_type,
                          BarSubscriptionType) and sub_key.subscription_type.bar_type == Bar.Time and sub_key.subscription_type.bar_size == BarSize.D1:
                inst = self.ref_data_mgr.get_inst(inst_id=sub_key.inst_id)
                symbol = inst.get_symbol(self.id())
                df = self.read_csv(symbol, '%s/%s.csv' % (self.path, symbol.lower()))
                dfs.append(df)

        df = pd.concat(dfs).sort_index(0, ascending=True)
        for index, row in df.iterrows():

            inst = self.ref_data_mgr.get_inst(symbol=row['Symbol'])
            range = sub_key_range[inst.inst_id]
            timestamp = DateUtils.datetime_to_unixtimemillis(index)
            if timestamp >= range[0] and timestamp < range[1]:
                self.data_event_bus.on_next(
                    Bar(inst_id=inst.inst_id,
                        timestamp=timestamp,
                        open=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        vol=row['Volume'],
                        adj_close=row['Adj Close'],
                        size=row['BarSize']))

    def unsubscribe_mktdata(self, *sub_keys):
        pass
