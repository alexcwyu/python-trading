import pandas as pd

from algotrader.model.market_data_pb2 import *
from algotrader.model.model_factory import ModelFactory
from algotrader.provider.feed import Feed
from algotrader.utils.date import datetime_to_unixtimemillis, datestr_to_unixtimemillis
from algotrader.utils.market_data import D1


class CSVDataFeed(Feed):
    dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')

    def __init__(self):
        super(CSVDataFeed, self).__init__()

    def _start(self, app_context):
        self.path = self._get_feed_config("path")
        self.ref_data_mgr = self.app_context.ref_data_mgr
        self.data_event_bus = self.app_context.event_bus.data_subject

    def _stop(self):
        pass

    def id(self):
        return Feed.CSV

    @staticmethod
    def read_csv(inst_id, provider_id, file):
        df = pd.read_csv(file, index_col='Date', parse_dates=['Date'], date_parser=CSVDataFeed.dateparse)
        df['InstId'] = inst_id
        df['ProviderId'] = provider_id
        df['BarSize'] = D1
        return df

    def subscribe_mktdata(self, *sub_reqs):
        self.__read_csv(*sub_reqs)

    def __read_csv(self, *sub_reqs):

        dfs = []
        sub_req_range = {sub_req.inst_id: (
            datestr_to_unixtimemillis(str(sub_req.from_date)),
            datestr_to_unixtimemillis(str(sub_req.to_date))) for
            sub_req in sub_reqs}

        for sub_req in sub_reqs:

            ## TODO support different format, e.g. BAR, Quote, Trade csv files
            if sub_req.type == MarketDataSubscriptionRequest.Bar and sub_req.bar_type == Bar.Time and sub_req.bar_size == D1:
                inst = self.ref_data_mgr.get_inst(inst_id=sub_req.inst_id)
                df = self.read_csv(sub_req.inst_id, sub_req.md_provider_id, '/mnt/data/dev/workspaces/python-trading/data/tradedata/%s.csv' % (
                    inst.symbol.lower()))
                dfs.append(df)

        df = pd.concat(dfs).sort_index(0, ascending=True)
        for index, row in df.iterrows():

            inst = self.ref_data_mgr.get_inst(row['InstId'])
            range = sub_req_range[inst.inst_id]
            timestamp = datetime_to_unixtimemillis(index)
            if timestamp >= range[0] and (not range[1] or timestamp < range[1]):
                self.data_event_bus.on_next(
                    ModelFactory.build_bar(
                        inst_id=inst.inst_id,
                        type=Bar.Time,
                        provider_id=row['ProviderId'],
                        timestamp=timestamp,
                        open=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        vol=row['Volume'],
                        adj_close=row['Adj Close'],
                        size=row['BarSize']))

    def unsubscribe_mktdata(self, *sub_reqs):
        pass
