"""
Created on 11/1/16
Author = jchan
"""
__author__ = 'jchan'

import re
import pandas as pd
import logging
from datetime import date
from algotrader.app import Application
from algotrader.chart.plotter import StrategyPlotter
from algotrader.config.app import ApplicationConfig, BacktestingConfig
from algotrader.config.persistence import PersistenceConfig
from algotrader.event.market_data import BarSize, BarType
from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock
from algotrader.provider.broker import Broker
from algotrader.config.feed import CSVFeedConfig
from algotrader.config.feed import PandasMemoryDataFeedConfig
from algotrader.strategy.alpha_formula import AlphaFormula3
from algotrader.strategy.vix_future import VIXFuture
from algotrader.provider.persistence import PersistenceMode
from algotrader.provider.persistence.data_store import DataStore
from algotrader.app.backtest_runner import BacktestRunner
from algotrader.config.builder import *
from algotrader.utils import logger


persistence_config = PersistenceConfig(None,
                                       DataStore.Mongo, PersistenceMode.RealTime,
                                       DataStore.Mongo, PersistenceMode.RealTime,
                                       DataStore.Mongo, PersistenceMode.RealTime,
                                       DataStore.Mongo, PersistenceMode.RealTime)


def test_vix():
    logger.setLevel(logging.DEBUG)
    symbols = ["VXF2015", "VXG2015", "VXH2015", "VXJ2015"]
    vix_data = {}

    with pd.HDFStore('/Users/jchan/workspace/data/temp/VX.h5') as store:
        for s in store.keys():
            sym = re.sub('/', '', s)
            df = store[s]
            df = df.reset_index()
            df['DateTime'] = df['Trade Date']
            df['Volume'] = df['Total Volume']
            df = df.set_index('DateTime')
            vix_data[sym] = df


    backtest_config = BacktestingConfig(id="test_vix", stg_id="vix6",
                                        stg_cls= 'algotrader.strategy.vix_future.VIXFuture',
                                        portfolio_id='test', portfolio_initial_cash=100000,
                                        instrument_ids=[125, 126, 127, 128, 129],
                                        subscription_types=[
                                            BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                                        from_date=date(2014, 11, 1), to_date=date(2015,4,1),
                                        broker_id=Broker.Simulator,
                                        feed_id=Feed.PandasMemory,
                                        #stg_configs={'qty': 10, 'contracts': [125, 126, 127, 128]},
                                        stg_configs={'qty': 10,
                                                     'exp_date_lb' : 10,
                                                     'exp_date_ub' : 180,
                                                     'short_entry_threshold' : 0.02,
                                                     'short_exit_threshold' : -0.01 },
                                        ref_data_mgr_type=RefDataManager.DB,
                                        persistence_config= backtest_mongo_persistance_config(),
                                        provider_configs=[MongoDBConfig, PandasMemoryDataFeedConfig(dict_df=vix_data)])


    app_context = ApplicationContext(app_config=backtest_config)
    BacktestRunner(True).start(app_context)

def main():
    # logger.setLevel(logging.DEBUG)
    symbols = ["BAC", "F", "FCX", "TWTR", "VALE", "PFE", "NOK", "ABBV", "PBR", "MRK", "KMI", "MRO", "KEY", "AMX", "COP", "C", "CVX", "BSX", "RF",  "CVS"]


    nyse_data = {}
    with pd.HDFStore('/Users/jchan/workspace/data/temp/NYSE.h5') as store:
        for s in store.keys():
            sym = re.sub('/', '', s)
            df = store[s]
            df['DateTime'] = pd.to_datetime(df['Date'] + 'T' + df['Time'])
            df = df.set_index('DateTime')
            nyse_data[sym] = df


    # backtest_config = BacktestingConfig(id="down2%-test-config", stg_id="down2%",
    #                                     stg_cls='algotrader.strategy.down_2pct_strategy.Down2PctStrategy',
    #                                     portfolio_id='test', portfolio_initial_cash=100000,
    #                                     instrument_ids=[3348],
    #                                     subscription_types=[
    #                                         BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
    #                                     from_date=date(2010, 1, 1), to_date=date.today(),
    #                                     broker_id=Broker.Simulator,
    #                                     feed_id=Feed.CSV,
    #                                     stg_configs={'qty': 1000},
    #                                     ref_data_mgr_type=RefDataManager.DB,
    #                                     persistence_config= backtest_mongo_persistance_config(),
    #                                     provider_configs=[MongoDBConfig(), CSVFeedConfig(path='../../data/tradedata')])

    backtest_config = BacktestingConfig(id="test_alpha", stg_id="alpha2",
                                        stg_cls='algotrader.strategy.alpha_formula.AlphaFormula3',
                                        portfolio_id='test', portfolio_initial_cash=100000,
                                        instrument_ids=[1248, 450, 1225],
                                        subscription_types=[
                                            BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.M5)],
                                        from_date=date(2016, 9, 1), to_date=date.today(),
                                        broker_id=Broker.Simulator,
                                        feed_id=Feed.PandasMemory,
                                        stg_configs={'qty': 1000},
                                        ref_data_mgr_type=RefDataManager.DB,
                                        persistence_config= backtest_mongo_persistance_config(),
                                        provider_configs=[MongoDBConfig, PandasMemoryDataFeedConfig(dict_df=nyse_data)])


    app_context = ApplicationContext(app_config=backtest_config)
    BacktestRunner(True).start(app_context)



if __name__ == "__main__":
    test_vix()
