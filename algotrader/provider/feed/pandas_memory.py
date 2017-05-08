from algotrader.provider.feed import PandasDataFeed, Feed
from algotrader import Context

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
            inst = insts[sub_req.inst_id]
            df = self.dict_of_df[sub_req.inst_id]
            df['InstId'] = sub_req.inst_id
            df['ProviderId'] = sub_req.md_provider_id
            df['BarSize'] = sub_req.bar_size

            dfs.append(df)
        return dfs

#
# if __name__ == "__main__":
#     dir = '/Users/jchan/workspace/data/Equity/US'
#     import pickle
#     from algotrader.trading.mock_ref_data import MockRefDataManager
#
#     symbols = ['SPY', 'VXX', 'XLV', 'XIV']
#     inst_df = pd.DataFrame({'name': symbols})
#     inst_df['type'] = 'ETF'
#     inst_df['symbol'] = inst_df['name']
#     inst_df['exch_id'] = "NYSE"
#     inst_df['ccy_id'] = 'USD'
#     inst_df['alt_symbols'] = ''
#     inst_df['alt_exch_id'] = ''
#     inst_df['sector'] = ''
#     inst_df['industry'] = ''
#     inst_df['put_call'] = ''
#     inst_df['expiry_date'] = ''
#     inst_df['und_inst_id'] = ''
#     inst_df['factor'] = ''
#     inst_df['strike'] = ''
#     inst_df['margin'] = ''
#     inst_df['inst_id'] = inst_df.index
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
#     # df_dict = {}
#     # filename = os.path.join(dir, 'etf.pkl')
#     # with open(filename, 'rb') as ifile:
#     #     df_dict = pickle.load(ifile)
#
#     start_date = datetime(2000, 1, 1)
#     num_days = 500
#     from datetime import timedelta
#     import numpy as np
#
#     dates = [start_date + timedelta(days=i) for i in range(num_days)]
#     sigma = 0.3
#     x0 = 100
#     dt = 1. / 252
#
#     from algotrader.utils.sde_sim import euler
#
#     drift0 = lambda x, t: 0.01 * x
#     diffusion0 = lambda x, t: 0.05 * x
#     drift1 = lambda x, t: -0.01 * x
#     diffusion1 = lambda x, t: 0.05 * x
#     drift2 = lambda x, t: -0.03 * x
#     diffusion2 = lambda x, t: 0.08 * x
#
#     simpath0 = euler(drift0, diffusion0, 1.0, 2.0, num_days, 1)
#     simpath1 = euler(drift1, diffusion1, 10.0, 2.0, num_days, 1)
#     simpath2 = euler(drift2, diffusion2, 100.0, 2.0, num_days, 1)
#
#     df0 = pd.DataFrame({"dates": dates,
#                         "Open": simpath0[0, :],
#                         "High": simpath0[0, :],
#                         "Low": simpath0[0, :],
#                         "Close": simpath0[0, :],
#                         "Volume": 10000 * np.ones(num_days)})
#
#     df0 = df0.set_index(keys="dates")
#
#     df1 = pd.DataFrame({"dates": dates,
#                         "Open": simpath1[0, :],
#                         "High": simpath1[0, :],
#                         "Low": simpath1[0, :],
#                         "Close": simpath1[0, :],
#                         "Volume": 10000 * np.ones(num_days)})
#
#     df1 = df1.set_index(keys="dates")
#
#     df2 = pd.DataFrame({"dates": dates,
#                         "Open": simpath2[0, :],
#                         "High": simpath2[0, :],
#                         "Low": simpath2[0, :],
#                         "Close": simpath2[0, :],
#                         "Volume": 10000 * np.ones(num_days)})
#
#     df2 = df2.set_index(keys="dates")
#
#     df_dict = {'SPY': df0,
#                'VXX': df1,
#                'XLV': df2}
#
#     feed = PandasMemoryDataFeed(df_dict, ref_data_mgr=mgr)
#
#     # today = date.today()
#     # sub_req = HistDataSubscriptionKey(inst_id=3, provider_id=PandasMemoryDataFeed.ID, data_type=Bar, bar_size=BarSize.D1,
#     #                                   from_date=datetime(2010, 1, 1), to_date=today)
#
#     sub_req0 = HistDataSubscriptionKey(inst_id=0, provider_id=PandasMemoryDataFeed.ID,
#                                        subscription_type=BarSubscriptionType(data_type=Bar, bar_size=BarSize.D1),
#                                        from_date=dates[0], to_date=dates[-1])
#
#     sub_req1 = HistDataSubscriptionKey(inst_id=1, provider_id=PandasMemoryDataFeed.ID,
#                                        subscription_type=BarSubscriptionType(data_type=Bar, bar_size=BarSize.D1),
#                                        from_date=dates[0], to_date=dates[-1])
#
#     sub_req2 = HistDataSubscriptionKey(inst_id=2, provider_id=PandasMemoryDataFeed.ID,
#                                        subscription_type=BarSubscriptionType(data_type=Bar, bar_size=BarSize.D1),
#                                        from_date=dates[0], to_date=dates[-1])
#     feed.subscribe_all_mktdata([sub_req0, sub_req1, sub_req2])
#
#     logger.setLevel(logging.DEBUG)
#     eventLogger = EventLogger()
#
#     feed.start()
