import logging

import pandas as pd
from datetime import date

from algotrader.event.event_bus import EventBus
from algotrader.event.event_handler import EventLogger
from algotrader.model.market_data_pb2 import *
from algotrader.model.model_factory import ModelFactory
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import HistDataSubscriptionKey
from algotrader.trading.ref_data import InMemoryRefDataManager
from algotrader.utils import logger
from algotrader.utils.clock import Clock
from algotrader.utils.market_data_utils import BarSize


class PandaH5DataFeed(Feed):
    """
    This is a class to make a data feed from dataframe we already have in memory
    """
    ID = "PandasMemory"

    def __init__(self, h5file, ref_data_mgr=None, data_event_bus=None):
        """
        :param h5file
        :param ref_data_mgr:
        :param data_event_bus:
        :return:
        """
        self.h5file = h5file
        self.__ref_data_mgr = ref_data_mgr if ref_data_mgr else InMemoryRefDataManager()
        self.__data_event_bus = data_event_bus if data_event_bus else EventBus.data_subject
        self.__sub_keys = []

        # feed_mgr.register(self)

    def start(self):
        self.__load_data(self.__sub_keys)
        for index, row in self.df.iterrows():
            ## TODO support bar filtering // from date, to date
            bar = self.process_row(index, row)
            self.__data_event_bus.on_next(bar)

    def stop(self):
        pass

    def id(self):
        return PandaH5DataFeed.ID

    def subscribe_all_mktdata(self, sub_keys):
        if isinstance(sub_keys, list):
            self.__sub_keys = self.__sub_keys + sub_keys
        else:
            self.__sub_keys.append(sub_keys)

    def subscribe_mktdata(self, sub_key):
        self.__sub_keys.append(sub_key)

    def process_row(self, index, row):
        inst = self.__ref_data_mgr.get_inst(symbol=row['Symbol'])
        return ModelFactory.build_bar(inst_id=inst.inst_id,
                                      type=Bar.Time,
                                      provider_id=self.id(),
                                      timestamp=Clock.datetime_to_unixtimemillis(index),
                                      open=row['Open'],
                                      high=row['High'],
                                      low=row['Low'],
                                      close=row['Close'],
                                      vol=row['Volume'],
                                      size=row['BarSize'])

    def __load_data(self, sub_keys):
        with pd.HDFStore(self.h5file) as store:
            self.dfs = []
            for sub_key in sub_keys:
                if not isinstance(sub_key, HistDataSubscriptionKey):
                    raise RuntimeError("only HistDataSubscriptionKey is supported!")
                if sub_key.data_type == Bar and sub_key.bar_type == Bar.Time and sub_key.bar_size == BarSize.D1:
                    inst = self.__ref_data_mgr.get_inst(inst_id=sub_key.inst_id)
                    symbol = inst.get_symbol(self.ID)

                    # df = web.DataReader("F", self.system, sub_key.from_date, sub_key.to_date)
                    # df = self.dict_of_df[symbol]
                    df = store[symbol]
                    df['Symbol'] = symbol
                    df['BarSize'] = int(BarSize.D1)

                    self.dfs.append(df)

            self.df = pd.concat(self.dfs).sort_index(0, ascending=True)
            # store.close()
            # for index, row in self.df.iterrows():
            # TODO support bar filtering // from date, to date
            # bar = self.process_row(index, row)
            # self.__data_event_bus.on_next(bar)

    def unsubscribe_mktdata(self, sub_key):
        pass


if __name__ == "__main__":
    dir = '/Users/jchan/workspace/data/Equity/US'
    from algotrader.trading.mock_ref_data import MockRefDataManager
    from algotrader.trading.mock_ref_data import build_inst_dataframe_from_list

    symbols = ['SPY', 'VXX', 'XLV', 'XIV']
    inst_df = build_inst_dataframe_from_list(symbols)

    #    ccy_id,name
    ccy_df = pd.DataFrame({"ccy_id": ["USD", "HKD"],
                           "name": ["US Dollar", "HK Dollar"]})

    exchange_df = pd.DataFrame({"exch_id": ["NYSE"],
                                "name": ["New York Stock Exchange"]})

    mgr = MockRefDataManager(inst_df, ccy_df, exchange_df)

    feed = PandaH5DataFeed('/Users/jchan/workspace/data/Equity/US/etf.h5', ref_data_mgr=mgr)

    today = date.today()
    startDate = date(2011, 1, 1)
    sub_key0 = HistDataSubscriptionKey(inst_id=0, provider_id=PandaH5DataFeed.ID, data_type=Bar, bar_size=BarSize.D1,
                                       from_date=startDate, to_date=today)

    sub_key1 = HistDataSubscriptionKey(inst_id=1, provider_id=PandaH5DataFeed.ID, data_type=Bar, bar_size=BarSize.D1,
                                       from_date=startDate, to_date=today)

    sub_key2 = HistDataSubscriptionKey(inst_id=2, provider_id=PandaH5DataFeed.ID, data_type=Bar, bar_size=BarSize.D1,
                                       from_date=startDate, to_date=today)

    feed.subscribe_all_mktdata([sub_key0, sub_key1, sub_key2])

    logger.setLevel(logging.DEBUG)
    eventLogger = EventLogger()

    feed.start()
