import pandas as pd

from algotrader import Context
from algotrader.provider.feed import Feed, PandasDataFeed
from algotrader.utils.market_data import build_bar_frame_id


class PandaDBDataFeed(PandasDataFeed):
    """
    This is a class to make a data feed from dataframe we already have in memory
    """

    def __init__(self):
        super(PandaDBDataFeed, self).__init__()

    def _start(self, app_context: Context) -> None:
        self.provider_id = self._get_feed_config("provider_id")

    def id(self):
        return Feed.PandasDB

    def _load_dataframes(self, insts, *sub_reqs):
        provider_id = self.provider_id
        dfs = []
        for sub_req in sub_reqs:
            inst = insts[sub_req.inst_id]
            frame_id = build_bar_frame_id(inst_id=inst.inst_id, size=sub_req.bar_size, provider_id=provider_id)
            algo_df = self.app_context.inst_data_mgr.get_frame(frame_id)
            df = algo_df.to_pd_dataframe()
            df['InstId'] = sub_req.inst_id
            df['ProviderId'] = sub_req.md_provider_id
            df['BarSize'] = sub_req.bar_size
            dfs.append(df)
        return dfs



