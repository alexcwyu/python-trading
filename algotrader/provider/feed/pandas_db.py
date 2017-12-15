import pandas as pd

from algotrader import Context
from algotrader.provider.feed import Feed, PandasDataFeed
from algotrader.utils.market_data import build_bar_frame_id
from algotrader.trading.series import Series
from algotrader.trading.data_frame import DataFrame


class PandaDBDataFeed(PandasDataFeed):
    """
    This is a class to make a data feed from dataframe we already have in memory
    """

    def __init__(self):
        super(PandaDBDataFeed, self).__init__(datetime_as_index=True)

    def _start(self, app_context: Context) -> None:
        self.store = app_context.get_data_store()
        self.provider_id = self._get_feed_config("provider_id")

    def id(self):
        return Feed.PandasDB

    def _load_dataframes(self, insts, *sub_reqs):
        provider_id = self.provider_id
        dfs = []
        for sub_req in sub_reqs:
            inst = insts[sub_req.inst_id]
            frame_id = build_bar_frame_id(inst_id=inst.inst_id, size=sub_req.bar_size, provider_id=provider_id)
            # algo_df = self.app_context.inst_data_mgr.get_frame(frame_id, provider_id=provider_id, inst_id=inst.inst_id)
            # df = algo_df.to_pd_dataframe()
            df = self._get_frame(frame_id).to_pd_dataframe()
            df['InstId'] = sub_req.inst_id
            df['ProviderId'] = sub_req.md_provider_id
            df['BarSize'] = sub_req.bar_size
            dfs.append(df)
        return dfs

    def _get_series(self, key):
        if type(key) != str:
            raise AssertionError()

        if self.store.obj_exist('series', key):
            proto_series = self.store.load_one('series', key)
            series = Series.from_proto_series(proto_series)
            return series

        else:
            raise RuntimeError("No series %s in database!" % key)


    def _get_frame(self, key):
        if type(key) != str:
            raise AssertionError()

        if self.store.obj_exist('frame', key):
            proto_frame = self.store.load_one('frame', key)
            series_list = [self._get_series(series_id) for series_id in proto_frame.series_id_list]
            series_dict = {series.col_id: series for series in series_list}
            frame = DataFrame.from_series_dict(series_dict)
            return frame

        else:
            raise RuntimeError("No dataframe %s in database!" % key)

