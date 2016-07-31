import abc
import logging
from datetime import date
from datetime import datetime

import pandas as pd

from algotrader.event.event_bus import EventBus
from algotrader.event.event_logger import EventLogger
from algotrader.event.market_data import Bar, BarType, BarSize
from algotrader.provider.provider import HistDataSubscriptionKey, Feed, feed_mgr
from algotrader.trading.ref_data import inmemory_ref_data_mgr
from algotrader.utils import logger
from algotrader.utils.clock import Clock


class PandasMemoryDataFeed(Feed):
    """
    This is a class to make a data feed from dataframe we already have in memory
    """
    ID = "PandasMemory"

    def __init__(self, dict_of_df, ref_data_mgr=None, data_event_bus=None):
        """
        :param dict_of_df: dictionary of pandas DataFrame with symbol as key
        :param ref_data_mgr:
        :param data_event_bus:
        :return:
        """
        self.dict_of_df = dict_of_df
        self.__ref_data_mgr = ref_data_mgr if ref_data_mgr else inmemory_ref_data_mgr
        self.__data_event_bus = data_event_bus if data_event_bus else EventBus.data_subject

        feed_mgr.register(self)

    def start(self):
        pass

    def stop(self):
        pass

    def id(self):
        return PandasMemoryDataFeed.ID

    def subscribe_all_mktdata(self, sub_keys):
        self.__load_data([sub_keys])

    def subscribe_mktdata(self, sub_key):
        self.__load_data([sub_key])

    def process_row(self, index, row):
        inst = self.__ref_data_mgr.get_inst(symbol=row['Symbol'])
        return Bar(inst_id=inst.inst_id,
                   timestamp=Clock.datetime_to_unixtimemillis(index),
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
            if sub_key.data_type == Bar and sub_key.bar_type == BarType.Time and sub_key.bar_size == BarSize.D1:
                inst = self.__ref_data_mgr.get_inst(inst_id=sub_key.inst_id)
                symbol = inst.get_symbol(self.ID)

                # df = web.DataReader("F", self.system, sub_key.from_date, sub_key.to_date)
                df = self.dict_of_df[symbol]
                df['Symbol'] = symbol
                df['BarSize'] = int(BarSize.D1)

                self.dfs.append(df)

        self.df = pd.concat(self.dfs).sort_index(0, ascending=True)

        for index, row in self.df.iterrows():
            ## TODO support bar filtering // from date, to date
            bar = self.process_row(index, row)
            self.__data_event_bus.on_next(bar)

    def unsubscribe_mktdata(self, sub_key):
        pass


if __name__ == "__main__":

    dir = '/Users/jchan/workspace/data/Equity/US'
    import pickle
    import os
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
    ccy_df = pd.DataFrame({ "ccy_id" : ["USD" , "HKD" ],
                            "name" : ["US Dollar", "HK Dollar"] })

    exchange_df = pd.DataFrame({"exch_id" : ["NYSE"],
                                "name" : ["New York Stock Exchange"]})

    mgr = MockRefDataManager(inst_df, ccy_df, exchange_df)

    # df_dict = {}
    # filename = os.path.join(dir, 'etf.pkl')
    # with open(filename, 'rb') as ifile:
    #     df_dict = pickle.load(ifile)

    start_date = date(2000, 1, 1)
    num_days = 1000
    from datetime import timedelta
    import numpy as np
    import math
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    sigma = 0.3
    x0 = 100
    dt = 1./252

    dW = np.random.normal(0,math.sqrt(dt), num_days)

    asset = []
    asset.append(x0)
    for i in xrange(1, num_days):
        xprev = asset[-1]
        x = xprev + xprev*0.02*dt + sigma*xprev*dW[i]
        asset.append(x)

    df = pd.DataFrame({"dates" : dates,
                       "Open" : asset,
                       "High" : asset,
                       "Low" : asset,
                       "Close" : asset,
                       "Volume" : 10000*np.ones(num_days)})

    df = df.set_index(keys="dates")

    df_dict = { 'SPY' : df,
                'VXX' : df,
                'XLV' : df,
                'XIV' : df}

    feed = PandasMemoryDataFeed(df_dict, ref_data_mgr=mgr)


    # today = date.today()
    # sub_key = HistDataSubscriptionKey(inst_id=3, provider_id=PandasMemoryDataFeed.ID, data_type=Bar, bar_size=BarSize.D1,
    #                                   from_date=datetime(2010, 1, 1), to_date=today)

    sub_key = HistDataSubscriptionKey(inst_id=3, provider_id=PandasMemoryDataFeed.ID, data_type=Bar, bar_size=BarSize.D1,
                                      from_date=dates[0], to_date=dates[-1])

    logger.setLevel(logging.DEBUG)
    eventLogger = EventLogger()

    feed.subscribe_mktdata(sub_key)
