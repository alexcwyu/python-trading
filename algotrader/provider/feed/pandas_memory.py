from algotrader import Context
from algotrader.provider.feed import PandasDataFeed, Feed


class PandasMemoryDataFeed(PandasDataFeed):
    """
    This is a class to make a data feed from dataframe we already have in memory
    """

    def __init__(self):
        super(PandasMemoryDataFeed, self).__init__()

    def _start(self, app_context: Context) -> None:
        pass

    def set_data_frame(self, dict_of_df):
        self.dict_of_df = dict_of_df

    def id(self):
        return Feed.PandasMemory

    def _load_dataframes(self, insts, *sub_reqs):
        dfs = []
        for sub_req in sub_reqs:
            df = self.dict_of_df[sub_req.inst_id]
            df['InstId'] = sub_req.inst_id
            df['ProviderId'] = sub_req.md_provider_id
            df['BarSize'] = sub_req.bar_size

            dfs.append(df)
        return dfs
