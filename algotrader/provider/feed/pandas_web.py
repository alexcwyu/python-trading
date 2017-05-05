import abc

import pandas as pd
from pandas_datareader import data

from algotrader.model.market_data_pb2 import *
from algotrader.model.model_factory import ModelFactory
from algotrader.provider.feed import Feed
from algotrader.utils.date_utils import DateUtils
from algotrader.utils.market_data_utils import BarSize


class PandasWebDataFeed(Feed):
    __metaclass__ = abc.ABCMeta

    def __init__(self, system):
        super(PandasWebDataFeed, self).__init__()
        self.system = system

    def _start(self, app_context):
        self.ref_data_mgr = self.app_context.ref_data_mgr
        self.data_event_bus = self.app_context.event_bus.data_subject

    def _stop(self):
        pass

    def subscribe_mktdata(self, *sub_reqs):
        self.__load_data(*sub_reqs)

    @abc.abstractmethod
    def process_row(self, row):
        raise NotImplementedError

    def __load_data(self, *sub_reqs):

        self.dfs = []
        for sub_req in sub_reqs:
            if not sub_req.from_date:
                raise RuntimeError("only HistDataSubscriptionKey is supported!")
            if sub_req.type == MarketDataSubscriptionRequest.Bar and sub_req.bar_type == Bar.Time and sub_req.bar_size == BarSize.D1:
                inst = self.__ref_data_mgr.get_inst(inst_id=sub_req.inst_id)
                symbol = inst.get_symbol(self.ID)

                # df = web.DataReader("F", self.system, sub_req.from_date, sub_req.to_date)
                df = data.DataReader("F", self.system, sub_req.from_date, sub_req.to_date)
                df['Symbol'] = symbol
                df['BarSize'] = int(BarSize.D1)

                self.dfs.append(df)

        self.df = pd.concat(self.dfs).sort_index(0, ascending=True)

        for index, row in self.df.iterrows():
            ## TODO support bar filtering // from date, to date
            bar = self.process_row(index, row)
            self.__data_event_bus.on_next(bar)

    def unsubscribe_mktdata(self, *sub_reqs):
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
        return ModelFactory.build_bar(inst_id=inst.inst_id,
                                      provider_id=self.id(),
                                      type=Bar.Time,
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

# if __name__ == "__main__":
#     feed = YahooDataFeed()
#
#     today = date.today()
#     sub_req = HistDataSubscriptionKey(inst_id=3, provider_id=YahooDataFeed.ID,
#                                       subscription_type=BarSubscriptionType(data_type=Bar.Time, bar_size=BarSize.D1),
#                                       from_date=datetime(2010, 1, 1), to_date=today)
#
#     logger.setLevel(logging.DEBUG)
#     eventLogger = EventLogger()
#
#     feed.subscribe_mktdata(sub_req)
