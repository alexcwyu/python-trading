import math
from datetime import datetime
from datetime import timedelta

import numpy as np
import pandas as pd

from algotrader.chart.plotter import StrategyPlotter
from algotrader.config.app import ApplicationConfig, BacktestingConfig
from algotrader.config.persistence import PersistenceConfig
from algotrader.event.market_data import BarSize, BarType
from algotrader.provider.broker import Broker
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.feed import Feed
from algotrader.provider.feed.pandas_memory import PandasMemoryDataFeed, PandasMemoryDataFeedConfig
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.strategy.sma_strategy import SMAStrategy
from algotrader.trading.instrument_data import InstrumentDataManager
from algotrader.trading.mock_ref_data import MockRefDataManager, build_inst_dataframe_from_list
from algotrader.trading.order_mgr import OrderManager
from algotrader.trading.portfolio import Portfolio
from algotrader.utils import clock
from algotrader.trading.ref_data import RefDataManager
from algotrader.config.persistence import MongoDBConfig
from algotrader.trading.context import ApplicationContext
from algotrader.config.builder import *
from algotrader.app import Application
from algotrader.app.backtest_runner import BacktestRunner

class MemoryBacktestRunner(Application):
    def __init__(self, isplot=False):
        self.isplot = isplot

    def init(self):
        self.app_config = self.app_context.app_config
        self.portfolio = self.app_context.portf_mgr.get_or_new_portfolio(self.app_config.portfolio_id,
                                                                         self.app_config.portfolio_initial_cash)

        self.initial_result = self.portfolio.get_result()

        self.app_context.add_startable(self.portfolio)

        self.strategy = self.app_context.stg_mgr.get_or_new_stg(self.app_config)
        self.app_context.add_startable(self.strategy)

    def run(self):
        self.app_context.start()
        self.strategy.start(self.app_context)
        if self.isplot:
            self.plot()

    def plot(self):
        print self.portfolio.get_result()

        # pyfolio
        rets = self.portfolio.get_return()
        # import pyfolio as pf
        # pf.create_returns_tear_sheet(rets)
        # pf.create_full_tear_sheet(rets)

        # build in plot
        plotter = StrategyPlotter(self.strategy)
        plotter.plot(instrument=self.app_context.app_config.instrument_ids[0])

def main():
    symbols = ['SPY', 'VXX', 'XLV', 'XIV']

    inst_df = build_inst_dataframe_from_list(symbols)
    ccy_df = pd.DataFrame({"ccy_id": ["USD", "HKD"],
                           "name": ["US Dollar", "HK Dollar"]})

    exchange_df = pd.DataFrame({"exch_id": ["NYSE"],
                                "name": ["New York Stock Exchange"]})
    mgr = MockRefDataManager(inst_df=inst_df, ccy_df=ccy_df, exch_df=exchange_df)

    portfolio = Portfolio(portf_id='test', cash=100000)

    start_date = datetime(2000, 1, 1)
    num_days = 3000

    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    sigma = 0.3
    x0 = 100
    dt = 1. / 252

    dW = np.random.normal(0, math.sqrt(dt), num_days)

    asset = []
    asset.append(x0)
    for i in xrange(1, num_days):
        xprev = asset[-1]
        x = xprev + xprev * 0.02 * dt + sigma * xprev * dW[i]
        asset.append(x)

    df = pd.DataFrame({"dates": dates,
                       "Open": asset,
                       "High": asset,
                       "Low": asset,
                       "Close": asset,
                       "Volume": 10000 * np.ones(num_days)})

    df = df.set_index(keys="dates")

    dict_df = {'SPY': df,
               'VXX': df,
               'XLV': df,
               'XIV': df}

    # feed = PandasMemoryDataFeed(dict_df, ref_data_mgr=mgr)
    feed = PandasMemoryDataFeed()

    broker = Simulator()

    instrument = 0

    backtest_config = BacktestingConfig(id="sma", stg_id='test',
                               stg_cls='algotrader.strategy.sma_strategy.SMAStrategy',
                               portfolio_id='test', portfolio_initial_cash=100000,
                               instrument_ids=[instrument],
                               subscription_types=[
                                   BarSubscriptionType(bar_type=BarType.Time,
                                                       bar_size=BarSize.D1)],
                               from_date=dates[0], to_date=dates[-1],
                               broker_id=Broker.Simulator,
                               feed_id=Feed.PandasMemory,
                               stg_configs={'qty': 1000},
                               ref_data_mgr_type=RefDataManager.DB,
                               persistence_config= backtest_mongo_persistance_config(),
                               provider_configs=PandasMemoryDataFeedConfig(dict_df=dict_df))

    app_context = ApplicationContext(app_config=backtest_config)

    BacktestRunner(True).start(app_context)
    # close = inst_data_mgr.get_series("Bar.%s.Time.86400" % instrument)

    # mgr.get_insts([instrument])
    # mgr.get_inst(instrument)

    # strategy = Down2PctStrategy("down2%", portfolio,
    #                             instrument=0, qty=1000,  trading_config=config, ref_data_mgr=mgr)

    # strategy = SMAStrategy("sma", stg_configs={'qty':1})
    #
    # runner = BacktestRunner(strategy)
    # runner.start()
    # print portfolio.get_result()

    # pyfolio
    # rets = strategy.get_portfolio().get_return()
    # import pyfolio as pf
    # pf.create_returns_tear_sheet(rets)
    # pf.create_full_tear_sheet(rets)

    # build in plot
    # plotter = StrategyPlotter(strategy)
    # plotter.plot(instrument=0)

    # import matplotlib.pyplot as plt
    # plt.show()

    # import talib
    # sma10 = talib.SMA(df.Close.values, 10)
    # sma25 = talib.SMA(df.Close.values, 25)
    #
    # #    signal = pd.Series(1*(sma10 > sma25),index=df.index.tz_localize("UTC"))
    # signal = pd.Series(1 * (sma10 > sma25), index=df.index)
    # target_rets = df["Close"].pct_change() * signal.shift(1)
    # target_rets.index = target_rets.index.tz_localize("UTC")
    # print target_rets.values[1:] - rets.values


if __name__ == "__main__":
    main()
