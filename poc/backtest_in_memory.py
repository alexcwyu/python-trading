
from datetime import date
from datetime import datetime
from datetime import timedelta

from algotrader.chart.plotter import StrategyPlotter
from algotrader.event.market_data import Bar, BarSize, BarType
from algotrader.provider.feed.csv_feed import CSVDataFeed
from algotrader.provider.feed.pandas_memory import PandasMemoryDataFeed
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.strategy.sma_strategy import SMAStrategy
from algotrader.strategy.down_2pct_strategy import Down2PctStrategy
from algotrader.strategy.strategy import BacktestingConfig
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.trading.mock_ref_data import MockRefDataManager, build_inst_dataframe_from_list
from algotrader.trading.order_mgr import order_mgr
from algotrader.trading.portfolio import Portfolio
from algotrader.utils import clock
import pandas as pd
import numpy as np
import math


class BacktestRunner(object):
    def __init__(self, stg):
        self.__stg = stg

    def start(self):
        clock.default_clock = clock.simluation_clock
        clock.simluation_clock.start()
        inst_data_mgr.start()
        order_mgr.start()

        self.__stg.start()


def main():
    symbols = ['SPY', 'VXX', 'XLV', 'XIV']

    inst_df = build_inst_dataframe_from_list(symbols)
    ccy_df = pd.DataFrame({ "ccy_id" : ["USD" , "HKD" ],
                            "name" : ["US Dollar", "HK Dollar"] })

    exchange_df = pd.DataFrame({"exch_id" : ["NYSE"],
                                "name" : ["New York Stock Exchange"]})
    mgr = MockRefDataManager(inst_df=inst_df,ccy_df=ccy_df,exch_df=exchange_df)

    portfolio = Portfolio(cash=100000)

    start_date = datetime(2000, 1, 1)
    num_days = 3000

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

    dict_df = { 'SPY' : df,
                'VXX' : df,
                'XLV' : df,
                'XIV' : df}


    feed = PandasMemoryDataFeed(dict_df, ref_data_mgr=mgr)

    broker = Simulator()

    config = BacktestingConfig(broker_id=Simulator.ID,
                               feed_id=PandasMemoryDataFeed.ID,
                               data_type=Bar,
                               bar_type=BarType.Time,
                               bar_size=BarSize.D1,
                               from_date=dates[0], to_date=dates[-1])


    instrument = 0
    close = inst_data_mgr.get_series("Bar.%s.Time.86400" % instrument)

    mgr.get_insts([instrument])
    mgr.get_inst(instrument)

    # strategy = Down2PctStrategy("down2%", portfolio,
    #                             instrument=0, qty=1000,  trading_config=config, ref_data_mgr=mgr)

    strategy = SMAStrategy("sma", portfolio, instrument=0, qty=1, trading_config=config)

    runner = BacktestRunner(strategy)
    runner.start()
    print portfolio.get_result()

    # pyfolio
    rets = strategy.get_portfolio().get_return()
    # import pyfolio as pf
    # pf.create_returns_tear_sheet(rets)
    # pf.create_full_tear_sheet(rets)

    # build in plot
    plotter = StrategyPlotter(strategy)
    plotter.plot(instrument=0)

    #import matplotlib.pyplot as plt
    #plt.show()

    import talib
    sma10 = talib.SMA(df.Close.values, 10)
    sma25 = talib.SMA(df.Close.values, 25)

#    signal = pd.Series(1*(sma10 > sma25),index=df.index.tz_localize("UTC"))
    signal = pd.Series(1*(sma10 > sma25),index=df.index)
    target_rets = df["Close"].pct_change()*signal.shift(1)
    target_rets.index = target_rets.index.tz_localize("UTC")
    print target_rets.values[1:] - rets.values

if __name__ == "__main__":
    main()
