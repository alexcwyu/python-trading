

from unittest import TestCase
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


class TestCompareWithFunctionalBacktest(TestCase):
    def test_with_sma(self):
        symbols = ['SPY', 'VXX', 'XLV', 'XIV']

        clock.simluation_clock.now()
        inst_df = build_inst_dataframe_from_list(symbols)
        ccy_df = pd.DataFrame({ "ccy_id" : ["USD" , "HKD" ],
                                "name" : ["US Dollar", "HK Dollar"] })

        exchange_df = pd.DataFrame({"exch_id" : ["NYSE"],
                                    "name" : ["New York Stock Exchange"]})
        mgr = MockRefDataManager(inst_df=inst_df,ccy_df=ccy_df,exch_df=exchange_df)

        init_cash = 1000000
        portfolio = Portfolio(cash=init_cash)

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

        lot_size = 10000
        strategy = SMAStrategy("sma", portfolio, instrument=0, qty=lot_size, trading_config=config)

        runner = BacktestRunner(strategy)
        runner.start()
        rets = strategy.get_portfolio().get_return()


        import talib
        sma10 = talib.SMA(df.Close.values, 10)
        sma25 = talib.SMA(df.Close.values, 25)

        signal = pd.Series(1*(sma10 > sma25),index=df.index)

        cash = []
        stock_value = []
        cash.append(init_cash)
        stock_value.append(0)
        for i in xrange(1, signal.shape[0]):
            cash.append(cash[-1] - lot_size*(signal[i]-signal[i-1])*df['Close'][i])
            stock_value.append(lot_size*signal[i]*df['Close'][i])

        target_port = pd.DataFrame({"cash": cash,
                                    "stock_value": stock_value})

        target_port["total_equity"] = target_port["cash"] + target_port["stock_value"]
        target_port["return"] = target_port["total_equity"].pct_change()

        try:
            np.testing.assert_almost_equal(target_port["return"].values[1:], rets.values, 5)
        except AssertionError as e:
            self.fail(e.message)



