import logging
from datetime import date

import pandas as pd

from algotrader.event.event_handler import EventLogger
from algotrader.event.market_data import Bar, BarType, BarSize
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import HistDataSubscriptionKey, BarSubscriptionType
from algotrader.utils import logger
from algotrader.utils.date_utils import DateUtils


class PandasMemoryDataFeed(Feed):
    """
    This is a class to make a data feed from dataframe we already have in memory
    """

    def __init__(self, app_context=None, dict_of_df=None):
        """
        :param dict_of_df: dictionary of pandas DataFrame with symbol as key
        :param ref_data_mgr:
        :param data_event_bus:
        :return:
        """
        super(PandasMemoryDataFeed, self).__init__()
        self.dict_of_df = dict_of_df
        self.app_context = app_context
        self.sub_keys = []

    def _start(self, app_context=None):
        self.ref_data_mgr = self.app_context.ref_data_mgr
        self.data_event_bus = self.app_context.event_bus.data_subject
        self.__load_data(self.sub_keys)
        for index, row in self.df.iterrows():
            ## TODO support bar filtering // from date, to date
            bar = self.process_row(index, row)
            self.data_event_bus.on_next(bar)

    def _stop(self):
        pass

    def id(self):
        return Feed.PandasMemory

    def subscribe_all_mktdata(self, sub_keys):
        if isinstance(sub_keys, list):
            self.sub_keys = self.sub_keys + sub_keys
        else:
            self.sub_keys.append(sub_keys)

    def subscribe_mktdata(self, sub_key):
        self.sub_keys.append(sub_key)

    def process_row(self, index, row):
        inst = self.ref_data_mgr.get_inst(symbol=row['Symbol'])
        return Bar(inst_id=inst.inst_id,
                   timestamp=DateUtils.datetime_to_unixtimemillis(index),
                   open=row['Open'],
                   high=row['High'],
                   low=row['Low'],
                   close=row['Close'],
                   vol=row['Volume'],
                   size=row['BarSize'])

    def __load_data(self, sub_keys):

        self.dfs = []
        for sub_key in sub_keys:
            if not isinstance(sub_key, HistDataSubscriptionKey):
                raise RuntimeError("only HistDataSubscriptionKey is supported!")
            if isinstance(sub_key.subscription_type,
                          BarSubscriptionType) and sub_key.subscription_type.bar_type == BarType.Time and sub_key.subscription_type.bar_size == BarSize.D1:
                inst = self.ref_data_mgr.get_inst(inst_id=sub_key.inst_id)
                symbol = inst.get_symbol(self.ID)

                # df = web.DataReader("F", self.system, sub_key.from_date, sub_key.to_date)
                df = self.dict_of_df[symbol]
                df['Symbol'] = symbol
                df['BarSize'] = int(BarSize.D1)

                self.dfs.append(df)

        self.df = pd.concat(self.dfs).sort_index(0, ascending=True)

        # for index, row in self.df.iterrows():
        # TODO support bar filtering // from date, to date
        # bar = self.process_row(index, row)
        # self.__data_event_bus.on_next(bar)

    def unsubscribe_mktdata(self, sub_key):
        pass


if __name__ == "__main__":
    dir = '/Users/jchan/workspace/data/Equity/US'
    import pickle
    from algotrader.trading.mock_ref_data import MockRefDataManager

    symbols = ['SPY', 'VXX', 'XLV', 'XIV']
    inst_df = pd.DataFrame({'name': symbols})
    inst_df['type'] = 'ETF'
    inst_df['symbol'] = inst_df['name']
    inst_df['exch_id'] = "NYSE"
    inst_df['ccy_id'] = 'USD'
    inst_df['alt_symbol'] = ''
    inst_df['alt_exch_id'] = ''
    inst_df['sector'] = ''
    inst_df['group'] = ''
    inst_df['put_call'] = ''
    inst_df['expiry_date'] = ''
    inst_df['und_inst_id'] = ''
    inst_df['factor'] = ''
    inst_df['strike'] = ''
    inst_df['margin'] = ''
    inst_df['inst_id'] = inst_df.index

    #    ccy_id,name
    ccy_df = pd.DataFrame({"ccy_id": ["USD", "HKD"],
                           "name": ["US Dollar", "HK Dollar"]})

    exchange_df = pd.DataFrame({"exch_id": ["NYSE"],
                                "name": ["New York Stock Exchange"]})

    mgr = MockRefDataManager(inst_df, ccy_df, exchange_df)

    # df_dict = {}
    # filename = os.path.join(dir, 'etf.pkl')
    # with open(filename, 'rb') as ifile:
    #     df_dict = pickle.load(ifile)

    start_date = date(2000, 1, 1)
    num_days = 500
    from datetime import timedelta
    import numpy as np

    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    sigma = 0.3
    x0 = 100
    dt = 1. / 252

    from algotrader.models.sde_sim import euler

    drift0 = lambda x, t: 0.01 * x
    diffusion0 = lambda x, t: 0.05 * x
    drift1 = lambda x, t: -0.01 * x
    diffusion1 = lambda x, t: 0.05 * x
    drift2 = lambda x, t: -0.03 * x
    diffusion2 = lambda x, t: 0.08 * x

    simpath0 = euler(drift0, diffusion0, 1.0, 2.0, num_days, 1)
    simpath1 = euler(drift1, diffusion1, 10.0, 2.0, num_days, 1)
    simpath2 = euler(drift2, diffusion2, 100.0, 2.0, num_days, 1)

    df0 = pd.DataFrame({"dates": dates,
                        "Open": simpath0[0, :],
                        "High": simpath0[0, :],
                        "Low": simpath0[0, :],
                        "Close": simpath0[0, :],
                        "Volume": 10000 * np.ones(num_days)})

    df0 = df0.set_index(keys="dates")

    df1 = pd.DataFrame({"dates": dates,
                        "Open": simpath1[0, :],
                        "High": simpath1[0, :],
                        "Low": simpath1[0, :],
                        "Close": simpath1[0, :],
                        "Volume": 10000 * np.ones(num_days)})

    df1 = df1.set_index(keys="dates")

    df2 = pd.DataFrame({"dates": dates,
                        "Open": simpath2[0, :],
                        "High": simpath2[0, :],
                        "Low": simpath2[0, :],
                        "Close": simpath2[0, :],
                        "Volume": 10000 * np.ones(num_days)})

    df2 = df2.set_index(keys="dates")

    df_dict = {'SPY': df0,
               'VXX': df1,
               'XLV': df2}

    feed = PandasMemoryDataFeed(df_dict, ref_data_mgr=mgr)

    # today = date.today()
    # sub_key = HistDataSubscriptionKey(inst_id=3, provider_id=PandasMemoryDataFeed.ID, data_type=Bar, bar_size=BarSize.D1,
    #                                   from_date=datetime(2010, 1, 1), to_date=today)

    sub_key0 = HistDataSubscriptionKey(inst_id=0, provider_id=PandasMemoryDataFeed.ID,
                                       subscription_type=BarSubscriptionType(data_type=Bar, bar_size=BarSize.D1),
                                       from_date=dates[0], to_date=dates[-1])

    sub_key1 = HistDataSubscriptionKey(inst_id=1, provider_id=PandasMemoryDataFeed.ID,
                                       subscription_type=BarSubscriptionType(data_type=Bar, bar_size=BarSize.D1),
                                       from_date=dates[0], to_date=dates[-1])

    sub_key2 = HistDataSubscriptionKey(inst_id=2, provider_id=PandasMemoryDataFeed.ID,
                                       subscription_type=BarSubscriptionType(data_type=Bar, bar_size=BarSize.D1),
                                       from_date=dates[0], to_date=dates[-1])
    feed.subscribe_all_mktdata([sub_key0, sub_key1, sub_key2])

    logger.setLevel(logging.DEBUG)
    eventLogger = EventLogger()

    feed.start()
