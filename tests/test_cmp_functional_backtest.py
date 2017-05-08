import math

import numpy as np
import pandas as pd
import talib
from unittest import TestCase

from algotrader.strategy.sma_strategy import SMAStrategy
from algotrader.trading.config import Config
from algotrader.trading.context import ApplicationContext
from algotrader.utils.ref_data import load_inst_from_df, load_ccy_from_df, load_exch_from_df, \
    build_inst_dataframe_from_list


class TestCompareWithFunctionalBacktest(TestCase):
    num_days = 3000
    dates = [i for i in range(num_days)]
    init_cash = 1000000

    def get_df(self, asset):
        df = pd.DataFrame({"dates": TestCompareWithFunctionalBacktest.dates,
                           "Open": asset,
                           "High": asset,
                           "Low": asset,
                           "Close": asset,
                           "Volume": 10000 * np.ones(TestCompareWithFunctionalBacktest.num_days)})

        df = df.set_index(keys="dates")

        return df

    def init_context(self, symbols, asset, config):

        self.app_context = ApplicationContext(config=config)

        inst_df = build_inst_dataframe_from_list(symbols)
        ccy_df = pd.DataFrame({"ccy_id": ["USD", "HKD"],
                               "name": ["US Dollar", "HK Dollar"]})
        exchange_df = pd.DataFrame({"exch_id": ["NYSE"],
                                    "name": ["New York Stock Exchange"]})

        self.app_context.start()

        datastore = self.app_context.get_data_store()
        load_exch_from_df(datastore, exchange_df)
        load_ccy_from_df(datastore, ccy_df)
        load_inst_from_df(datastore, inst_df)

        self.portfolio = self.app_context.portf_mgr.new_portfolio(portf_id='test2',
                                                                  initial_cash=TestCompareWithFunctionalBacktest.init_cash)
        self.portfolio.start(self.app_context)

    def tearDown(self):
        self.app_context.stop()

    def test_with_sma(self):

        sigma = 0.3
        x0 = 100
        dt = 1. / 252
        dW = np.random.normal(0, math.sqrt(dt), TestCompareWithFunctionalBacktest.num_days)

        asset = []
        asset.append(x0)
        for i in range(1, TestCompareWithFunctionalBacktest.num_days):
            xprev = asset[-1]
            x = xprev + xprev * 0.02 * dt + sigma * xprev * dW[i]
            asset.append(x)

        instrument = 0

        lot_size = 10000

        symbols = ['SPY', 'VXX', 'XLV', 'XIV']
        dict_df = {}

        self.df = self.get_df(asset=asset)
        for symbol in symbols:
            dict_df[symbol] = self.df

        config = Config({
            "Application": {
                "type": "BackTesting",

                "clockId": "Simulation",

                "dataStoreId": "InMemory",
                "persistenceMode": "Disable",
                "createDBAtStart": True,
                "deleteDBAtStop": False,

                "feedId": "PandasMemory",
                "brokerId": "Simulator",
                "portfolioId": "test2",
                "stg": "down2%",
                "stgCls": "algotrader.strategy.down_2pct_strategy.Down2PctStrategy",
                "instrumentIds": ["0"],
                "subscriptionTypes": ["Bar.Yahoo.Time.D1"],

                "fromDate": TestCompareWithFunctionalBacktest.dates[0],
                "toDate": TestCompareWithFunctionalBacktest.dates[-1],
                "plot": False
            },
            "DataStore": {"InMemory":
                {
                    "file": "../data/algotrader_db.p",
                    "instCSV": "../data/refdata/instrument.csv",
                    "ccyCSV": "../data/refdata/ccy.csv",
                    "exchCSV": "../data/refdata/exch.csv"
                }
            },

            "Strategy": {
                "down2%": {
                    "qty": lot_size
                }
            }

        })

        self.init_context(symbols=symbols, asset=asset, config=config)

        feed = self.app_context.get_feed()
        feed.set_data_frame(dict_df)
        close = self.app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % instrument)
        close.start(self.app_context)

        strategy = SMAStrategy("sma")
        strategy.start(self.app_context)

        rets = strategy.get_portfolio().get_return()
        bt_result = strategy.get_portfolio().get_result()

        sma10 = talib.SMA(self.df.Close.values, 10)
        sma25 = talib.SMA(self.df.Close.values, 25)
        signal = pd.Series(1 * (sma10 > sma25), index=self.df.index)

        cash = []
        stock_value = []
        cash.append(TestCompareWithFunctionalBacktest.init_cash)
        stock_value.append(0)
        for i in range(1, signal.shape[0]):
            cash.append(cash[-1] - lot_size * (signal[i] - signal[i - 1]) * self.df['Close'][i])
            stock_value.append(lot_size * signal[i] * self.df['Close'][i])

        target_port = pd.DataFrame({"cash": cash,
                                    "stock_value": stock_value})

        target_port["total_equity"] = target_port["cash"] + target_port["stock_value"]
        target_port["return"] = target_port["total_equity"].pct_change()

        try:
            np.testing.assert_almost_equal(target_port["return"].values[1:], rets.values, 5)
        except AssertionError as e:
            self.fail(e.message)
        finally:
            strategy.stop()

            # def test_merton_baby_optimal(self):
            #     sigma = 0.3
            #     x0 = 100
            #     dt = 1. / 252
            #
            #     arate = 0.05
            #     vol = 0.3
            #
            #     from algotrader.models.sde_sim import euler
            #
            #     # simulate a Geometric Brownian Motion
            #     drift = lambda x, t: arate * x
            #     diffusion = lambda x, t: vol * x
            #
            #     sim_paths = euler(drift, diffusion, 100.0, 10.0, 3000, 10)
            #     asset = sim_paths[1, :]  # pick the first sim path
            #
            #     instrument = 0
            #
            #     symbols=['DUMMY']
            #     dict_df = {}
            #     for symbol in symbols:
            #         dict_df[symbol] = self.get_df(asset=asset)
            #
            #     config = BacktestingConfig(stg_id='mtnb', portfolio_id='test2',
            #                                instrument_ids=[instrument],
            #                                subscription_types=[BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
            #                                from_date=TestCompareWithFunctionalBacktest.dates[0],
            #                                to_date=TestCompareWithFunctionalBacktest.dates[-1],
            #                                broker_id=Broker.Simulator,
            #                                feed_id=Feed.PandasMemory,
            #                                stg_configs={'arate': arate, 'vol': vol},
            #                                ref_data_mgr_type= None, persistence_config= None,
            #                                provider_configs = PandasMemoryDataFeedConfig(dict_df=dict_df))
            #
            #     self.init_context(symbols=symbols, asset=asset, app_config=config)
            #
            #     close = self.app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % instrument)
            #     close.start(self.app_context)
            #
            #     strategy = MertonOptimalBaby("mtnb")
            #     strategy.start(app_context=self.app_context)
            #
            #     rets = strategy.get_portfolio().get_return()
            #
            #     test_port_df = strategy.get_portfolio().get_series()
            #     test_port_df = pd.DataFrame(test_port_df)
            #     # print test_port_df.head(5)
            #
            #     optimal_weight = arate / vol ** 2
            #
            #     cash = []
            #     stock_value = []
            #     num_shares = []
            #     total_equity = []
            #     stock_value.append(TestCompareWithFunctionalBacktest.init_cash * optimal_weight)
            #     num_shares.append(stock_value[-1] / asset[0])
            #     cash.append(TestCompareWithFunctionalBacktest.init_cash - stock_value[-1])
            #     total_equity.append(TestCompareWithFunctionalBacktest.init_cash)
            #
            #     for i in xrange(1, asset.shape[0]):
            #         curr_stock_value = num_shares[-1] * asset[i]
            #         curr_total_equity = cash[-1] + curr_stock_value
            #         new_stock_value = curr_total_equity * optimal_weight
            #         new_num_shares = new_stock_value / asset[i]
            #         new_cash = curr_total_equity - new_stock_value
            #
            #         stock_value.append(new_stock_value)
            #         num_shares.append(new_num_shares)
            #         cash.append(new_cash)
            #         total_equity.append(curr_total_equity)
            #
            #     target_port_df = pd.DataFrame({"cash": cash,
            #                                    "stock_value": stock_value,
            #                                    "total_equity": total_equity
            #                                    })
            #
            #     target_port_df["return"] = target_port_df["total_equity"].pct_change()
            #
            #     # print target_port_df.head(5)
            #
            #     try:
            #         np.testing.assert_almost_equal(target_port_df["return"].values[1:], rets.values, 5)
            #         np.testing.assert_almost_equal(target_port_df["cash"].values, test_port_df["cash"].values, 5)
            #         np.testing.assert_almost_equal(target_port_df["stock_value"].values, test_port_df["stock_value"].values, 5)
            #     except AssertionError as e:
            #         self.fail(e.message)
            #     finally:
            #         strategy.stop()
