

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
from algotrader.strategy.merton_optimal import MertonOptimalBaby
from algotrader.trading.config import BacktestingConfig
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.trading.mock_ref_data import MockRefDataManager, build_inst_dataframe_from_list
from algotrader.trading.order_mgr import order_mgr
from algotrader.trading.portfolio import Portfolio
from algotrader.utils import clock
import pandas as pd
import numpy as np
import math
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.portfolio_mgr import portf_mgr


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
    def tearDown(self):
        clock.simluation_clock.reset()
        inst_data_mgr.clear()
        portf_mgr.clear()

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
        portfolio = Portfolio(portf_id='test2', cash=init_cash)

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

        instrument = 0

        config = BacktestingConfig(portfolio_id='test2',
                               instrument_ids=[instrument],
                               subscription_types = [BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                               from_date=dates[0], to_date=dates[-1],
                               broker_id=Simulator.ID,
                               feed_id=PandasMemoryDataFeed.ID)

        close = inst_data_mgr.get_series("Bar.%s.Time.86400" % instrument)
        mgr.get_insts([instrument])
        mgr.get_inst(instrument)

        lot_size = 10000
        strategy = SMAStrategy("sma", qty=lot_size, trading_config=config)

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


    def test_merton_baby_optimal(self):
        symbols = ['DUMMY']

        inst_df = build_inst_dataframe_from_list(symbols)
        ccy_df = pd.DataFrame({ "ccy_id" : ["USD" , "HKD" ],
                                "name" : ["US Dollar", "HK Dollar"] })

        exchange_df = pd.DataFrame({"exch_id": ["NYSE"],
                                    "name": ["New York Stock Exchange"]})
        mgr = MockRefDataManager(inst_df=inst_df, ccy_df=ccy_df, exch_df=exchange_df)

        init_cash = 1000000
        portfolio = Portfolio(portf_id='test', cash=init_cash)

        start_date = datetime(2000, 1, 1)
        num_days = 3000

        dates = [start_date + timedelta(days=i) for i in range(num_days)]
        sigma = 0.3
        x0 = 100
        dt = 1./252

        arate = 0.05
        vol = 0.3

        from algotrader.models.sde_sim import euler

        # simulate a Geometric Brownian Motion
        drift = lambda x, t: arate*x
        diffusion = lambda x, t: vol*x

        sim_paths = euler(drift, diffusion, 100.0, 10.0, 3000, 10)
        asset = sim_paths[1,:] # pick the first sim path

        df = pd.DataFrame({"dates" : dates,
                           "Open" : asset,
                           "High" : asset,
                           "Low" : asset,
                           "Close" : asset,
                           "Volume" : 10000*np.ones(num_days)})

        df = df.set_index(keys="dates")

        dict_df = {'DUMMY': df}

        feed = PandasMemoryDataFeed(dict_df, ref_data_mgr=mgr)
        broker = Simulator()

        instrument = 0
        config = BacktestingConfig(portfolio_id='test',
                               instrument_ids=[instrument],
                               subscription_types = [BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                               from_date=dates[0], to_date=dates[-1],
                               broker_id=Simulator.ID,
                               feed_id=PandasMemoryDataFeed.ID)


        close = inst_data_mgr.get_series("Bar.%s.Time.86400" % instrument)

        strategy = MertonOptimalBaby("mtnb", arate=arate, vol=vol, trading_config=config)

        runner = BacktestRunner(strategy)
        runner.start()
        rets = strategy.get_portfolio().get_return()
        test_port_df = strategy.get_portfolio().get_series()
        test_port_df = pd.DataFrame(test_port_df)
        # print test_port_df.head(5)

        optimal_weight = arate / vol**2

        cash = []
        stock_value = []
        num_shares = []
        total_equity = []
        stock_value.append(init_cash*optimal_weight)
        num_shares.append(stock_value[-1]/asset[0])
        cash.append(init_cash-stock_value[-1])
        total_equity.append(init_cash)

        for i in xrange(1, asset.shape[0]):
            curr_stock_value = num_shares[-1]*asset[i]
            curr_total_equity = cash[-1] + curr_stock_value
            new_stock_value = curr_total_equity*optimal_weight
            new_num_shares = new_stock_value / asset[i]
            new_cash = curr_total_equity - new_stock_value

            stock_value.append(new_stock_value)
            num_shares.append(new_num_shares)
            cash.append(new_cash)
            total_equity.append(curr_total_equity)

        target_port_df = pd.DataFrame({"cash": cash,
                                    "stock_value": stock_value,
                                    "total_equity": total_equity
                                    })

        target_port_df["return"] = target_port_df["total_equity"].pct_change()

        # print target_port_df.head(5)

        try:
            np.testing.assert_almost_equal(target_port_df["return"].values[1:], rets.values, 5)
            np.testing.assert_almost_equal(target_port_df["cash"].values, test_port_df["cash"].values, 5)
            np.testing.assert_almost_equal(target_port_df["stock_value"].values, test_port_df["stock_value"].values, 5)
        except AssertionError as e:
            self.fail(e.message)


