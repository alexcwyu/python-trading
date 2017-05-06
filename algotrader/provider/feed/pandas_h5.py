import pandas as pd

from algotrader.provider.feed import Feed, PandasDataFeed


class PandaH5DataFeed(PandasDataFeed):
    """
    This is a class to make a data feed from dataframe we already have in memory
    """

    def __init__(self):
        super(PandaH5DataFeed, self).__init__()

    def _start(self, app_context):
        self.h5file = self._get_feed_config("path")

    def id(self):
        return Feed.PandasH5

    def _load_dataframes(self, insts, *sub_reqs):
        dfs = []
        with pd.HDFStore(self.h5file) as store:
            for sub_req in sub_reqs:
                inst = insts[sub_req.inst_id]
                df = store[sub_req.inst_id]
                df['InstId'] = sub_req.inst_id
                df['ProviderId'] = sub_req.md_provider_id
                df['BarSize'] = sub_req.bar_size
                dfs.append(df)
        return dfs

#
# if __name__ == "__main__":
#     dir = '/Users/jchan/workspace/data/Equity/US'
#     from algotrader.trading.mock_ref_data import MockRefDataManager
#     from algotrader.trading.mock_ref_data import build_inst_dataframe_from_list
#
#     symbols = ['SPY', 'VXX', 'XLV', 'XIV']
#     inst_df = build_inst_dataframe_from_list(symbols)
#
#     #    ccy_id,name
#     ccy_df = pd.DataFrame({"ccy_id": ["USD", "HKD"],
#                            "name": ["US Dollar", "HK Dollar"]})
#
#     exchange_df = pd.DataFrame({"exch_id": ["NYSE"],
#                                 "name": ["New York Stock Exchange"]})
#
#     mgr = MockRefDataManager(inst_df, ccy_df, exchange_df)
#
#     feed = PandaH5DataFeed('/Users/jchan/workspace/data/Equity/US/etf.h5', ref_data_mgr=mgr)
#
#     today = date.today()
#     startDate = date(2011, 1, 1)
#     sub_req0 = HistDataSubscriptionKey(inst_id=0, provider_id=PandaH5DataFeed.ID, data_type=Bar, bar_size=BarSize.D1,
#                                        from_date=startDate, to_date=today)
#
#     sub_req1 = HistDataSubscriptionKey(inst_id=1, provider_id=PandaH5DataFeed.ID, data_type=Bar, bar_size=BarSize.D1,
#                                        from_date=startDate, to_date=today)
#
#     sub_req2 = HistDataSubscriptionKey(inst_id=2, provider_id=PandaH5DataFeed.ID, data_type=Bar, bar_size=BarSize.D1,
#                                        from_date=startDate, to_date=today)
#
#     feed.subscribe_all_mktdata([sub_req0, sub_req1, sub_req2])
#
#     logger.setLevel(logging.DEBUG)
#     eventLogger = EventLogger()
#
#     feed.start()
