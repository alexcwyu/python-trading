import abc

import pandas as pd

from algotrader.model.market_data_pb2 import *
from algotrader.model.model_factory import ModelFactory
from algotrader.provider import Provider
from algotrader.utils.date import datestr_to_unixtimemillis, datetime_to_unixtimemillis
from algotrader.utils.market_data import D1


class Feed(Provider):
    CSV = "CSV"
    PandasMemory = "PandasMemory"
    PandasH5 = "PandasH5"
    PandasWeb = "PandasWeb"
    Yahoo = "Yahoo"
    Google = "Google"
    Quandl = "Quandl"

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Provider, self).__init__()

    @abc.abstractmethod
    def subscribe_mktdata(self, *sub_reqs):
        raise NotImplementedError()

    @abc.abstractmethod
    def unsubscribe_mktdata(self, *sub_reqs):
        raise NotImplementedError()

    def _get_feed_config(self, path: str, default=None):
        return self.app_context.config.get_feed_config(self.id(), path, default=default)


class PandasDataFeed(Feed):
    __metaclass__ = abc.ABCMeta

    def subscribe_mktdata(self, *sub_reqs):
        self._verify_subscription(*sub_reqs);
        sub_req_ranges = {}
        insts = {}
        for sub_req in sub_reqs:
            insts[sub_req.inst_id] = self.app_context.ref_data_mgr.get_inst(inst_id=sub_req.inst_id)
            sub_req_ranges[sub_req.inst_id] = (
                datestr_to_unixtimemillis(str(sub_req.from_date)), datestr_to_unixtimemillis(str(sub_req.to_date)))

        dfs = self._load_dataframes(insts, *sub_reqs)
        self._publish(dfs, sub_req_ranges, insts)

    def _verify_subscription(self, *sub_reqs):
        for sub_req in sub_reqs:
            if not sub_req.from_date or sub_req.type != MarketDataSubscriptionRequest.Bar or sub_req.bar_type != Bar.Time or sub_req.bar_size != D1:
                raise RuntimeError("only HistDataSubscriptionKey is supported!")

    def _within_range(self, inst_id, timestamp, sub_req_ranges):
        sub_req_range = sub_req_ranges[inst_id]
        return timestamp >= sub_req_range[0] and (not sub_req_range[1] or timestamp < sub_req_range[1])

    def _publish(self, dfs, sub_req_ranges, insts):
        df = pd.concat(dfs).sort_index(0, ascending=True)

        for index, row in df.iterrows():
            inst = insts[row['InstId']]
            timestamp = datetime_to_unixtimemillis(index)
            if self._within_range(row['InstId'], timestamp, sub_req_ranges):
                bar = self._build_bar(row, timestamp)
                self.app_context.event_bus.data_subject.on_next(bar)

    def _build_bar(self, row, timestamp) -> Bar:
        return ModelFactory.build_bar(
            inst_id=row['InstId'],
            type=Bar.Time,
            provider_id=row['ProviderId'],
            timestamp=timestamp,
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
            vol=row['Volume'],
            adj_close=row['Adj Close'] if 'Adj Close' in row else None,
            size=row['BarSize'])

    @abc.abstractmethod
    def _load_dataframes(self, insts, *sub_reqs):
        raise NotImplementedError()

    def unsubscribe_mktdata(self, *sub_reqs):
        pass

    def _stop(self):
        pass
