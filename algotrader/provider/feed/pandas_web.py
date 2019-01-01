import abc

from pandas_datareader import data

from algotrader import Context
from algotrader.provider.feed import Feed, PandasDataFeed
from algotrader.utils.date import *


class PandasWebDataFeed(PandasDataFeed):
    Supported = set(['Yahoo', 'Google'])

    def __init__(self):
        super(PandasWebDataFeed, self).__init__()

    def _start(self, app_context: Context) -> None:
        pass

    def id(self):
        return Feed.PandasWeb

    @abc.abstractmethod
    def process_row(self, row):
        raise NotImplementedError

    def _verify_subscription(self, *sub_reqs):
        super(PandasWebDataFeed, self)._verify_subscription(*sub_reqs)
        for sub_req in sub_reqs:
            if not sub_req.md_provider_id or sub_req.md_provider_id not in PandasWebDataFeed.Supported:
                raise RuntimeError("only yahoo and goolge is supported!")

    def _load_dataframes(self, insts, *sub_reqs):
        dfs = []
        for sub_req in sub_reqs:
            inst = insts[sub_req.inst_id]
            df = data.DataReader(inst.symbol.lower(), sub_req.md_provider_id.lower(),
                                 datestr_to_date(str(sub_req.from_date)),
                                 datestr_to_date(str(sub_req.to_date)))
            df['InstId'] = sub_req.inst_id
            df['ProviderId'] = sub_req.md_provider_id
            df['BarSize'] = sub_req.bar_size
            dfs.append(df)
        return dfs
