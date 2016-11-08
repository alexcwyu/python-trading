import abc
import logging
from datetime import date
from datetime import datetime

import pandas as pd
from pandas_datareader import data

from algotrader.event.event_handler import EventLogger
from algotrader.event.market_data import Bar, BarType, BarSize
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import HistDataSubscriptionKey, BarSubscriptionType
from algotrader.utils import logger
from algotrader.utils.date_utils import DateUtils


class PandasWebDataFeed(Feed):
    __metaclass__ = abc.ABCMeta

    def __init__(self, system):
        super(PandasWebDataFeed, self).__init__()
        self.system = system

    def _start(self, app_context, **kwargs):
        self.ref_data_mgr = self.app_context.ref_data_mgr
        self.data_event_bus = self.app_context.event_bus.data_subject

    def _stop(self):
        pass

    def subscribe_mktdata(self, *sub_keys):
        self.__load_data(*sub_keys)

    @abc.abstractmethod
    def process_row(self, row):
        raise NotImplementedError

    def __load_data(self, sub_keys):

        self.dfs = []
        for sub_key in sub_keys:
            if not isinstance(sub_key, HistDataSubscriptionKey):
                raise RuntimeError("only HistDataSubscriptionKey is supported!")
            if isinstance(sub_key.subscription_type,
                          BarSubscriptionType) and sub_key.subscription_type.bar_type == BarType.Time and sub_key.subscription_type.bar_size == BarSize.D1:
                inst = self.__ref_data_mgr.get_inst(inst_id=sub_key.inst_id)
                symbol = inst.get_symbol(self.ID)

                # df = web.DataReader("F", self.system, sub_key.from_date, sub_key.to_date)
                df = data.DataReader("F", self.system, sub_key.from_date, sub_key.to_date)
                df['Symbol'] = symbol
                df['BarSize'] = int(BarSize.D1)

                self.dfs.append(df)

        self.df = pd.concat(self.dfs).sort_index(0, ascending=True)

        for index, row in self.df.iterrows():
            ## TODO support bar filtering // from date, to date
            bar = self.process_row(index, row)
            self.__data_event_bus.on_next(bar)

    def unsubscribe_mktdata(self, *sub_keys):
        pass

    def id(self):
        return Feed.PandasWeb


class YahooDataFeed(PandasWebDataFeed):
    URL = 'http://real-chart.finance.yahoo.com/table.csv?s=%s&d=%s&e=%s&f=%s&g=d&a=%s&b=%s&c=%s&ignore=.csv'

    def __init__(self):
        super(YahooDataFeed, self).__init__(system='yahoo')

    def id(self):
        return Feed.Yahoo

    def process_row(self, index, row):
        inst = self.__ref_data_mgr.get_inst(symbol=row['Symbol'])
        return Bar(inst_id=inst.inst_id,
                   timestamp=DateUtils.datetime_to_unixtimemillis(index),
                   open=row['Open'],
                   high=row['High'],
                   low=row['Low'],
                   close=row['Close'],
                   vol=row['Volume'],
                   adj_close=row['Adj Close'],
                   size=row['BarSize'])


class GoogleDataFeed(PandasWebDataFeed):
    def __init__(self):
        super(GoogleDataFeed, self).__init__(system='google')

    def id(self):
        return Feed.Google

    def process_row(self, index, row):
        inst = self.__ref_data_mgr.get_inst(symbol=row['Symbol'])
        return Bar(inst_id=inst.inst_id,
                   timestamp=DateUtils.datetime_to_unixtimemillis(index),
                   open=row['Open'],
                   high=row['High'],
                   low=row['Low'],
                   close=row['Close'],
                   vol=row['Volume'],
                   size=row['BarSize'])


if __name__ == "__main__":
    feed = YahooDataFeed()

    today = date.today()
    sub_key = HistDataSubscriptionKey(inst_id=3, provider_id=YahooDataFeed.ID,
                                      subscription_type=BarSubscriptionType(data_type=Bar, bar_size=BarSize.D1),
                                      from_date=datetime(2010, 1, 1), to_date=today)

    logger.setLevel(logging.DEBUG)
    eventLogger = EventLogger()

    feed.subscribe_mktdata(sub_key)
