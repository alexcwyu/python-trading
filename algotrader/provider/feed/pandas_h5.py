import pandas as pd

from algotrader import Context
from algotrader.provider.feed import Feed, PandasDataFeed


class PandaH5DataFeed(PandasDataFeed):
    """
    This is a class to make a data feed from dataframe we already have in memory
    """

    def __init__(self):
        super(PandaH5DataFeed, self).__init__()

    def _start(self, app_context: Context) -> None:
        self.h5file = self._get_feed_config("path")

    def id(self):
        return Feed.PandasH5

    def _load_dataframes(self, insts, *sub_reqs):
        dfs = []
        with pd.HDFStore(self.h5file) as store:
            for sub_req in sub_reqs:
                df = store[sub_req.inst_id]
                df['InstId'] = sub_req.inst_id
                df['ProviderId'] = sub_req.md_provider_id
                df['BarSize'] = sub_req.bar_size
                dfs.append(df)
        return dfs
