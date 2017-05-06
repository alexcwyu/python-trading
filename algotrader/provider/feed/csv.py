import pandas as pd

from algotrader.provider.feed import Feed, PandasDataFeed


class CSVDataFeed(PandasDataFeed):
    dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')

    def __init__(self):
        super(CSVDataFeed, self).__init__()

    def _start(self, app_context):
        self.path = self._get_feed_config("path")

    def id(self):
        return Feed.CSV

    def _load_dataframes(self, insts, *sub_reqs):
        dfs = []
        for sub_req in sub_reqs:
            inst = insts[sub_req.inst_id]
            df = pd.read_csv('%s/%s.csv' % (self.path, inst.symbol.lower()), index_col='Date', parse_dates=['Date'],
                             date_parser=CSVDataFeed.dateparse)
            df['InstId'] = sub_req.inst_id
            df['ProviderId'] = sub_req.md_provider_id
            df['BarSize'] = sub_req.bar_size
            dfs.append(df)
        return dfs
