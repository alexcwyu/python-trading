from datetime import datetime
from datetime import timedelta

import numpy as np
import pandas as pd
from algotrader.event.market_data import BarSize, BarType

from algotrader.chart.plotter import StrategyPlotter
from algotrader.config.app import BacktestingConfig
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.feed.pandas_memory import PandasMemoryDataFeed
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.strategy.pair_trading import PairTradingWithOUSpread
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.trading.mock_ref_data import MockRefDataManager, build_inst_dataframe_from_list
from algotrader.trading.order_mgr import order_mgr
from algotrader.trading.portfolio import Portfolio
from algotrader.utils import clock
from algotrader.utils.sde_sim import euler


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
    symbols = ['XXX', 'YYY']

    inst_df = build_inst_dataframe_from_list(symbols)
    ccy_df = pd.DataFrame({"ccy_id": ["USD", "HKD"],
                           "name": ["US Dollar", "HK Dollar"]})

    exchange_df = pd.DataFrame({"exch_id": ["NYSE"],
                                "name": ["New York Stock Exchange"]})

    mgr = MockRefDataManager(inst_df=inst_df, ccy_df=ccy_df, exch_df=exchange_df)
    portfolio = Portfolio(cash=100000)

    start_date = datetime(2000, 1, 1)
    num_days = 300

    dates = [start_date + timedelta(days=i) for i in range(num_days)]

    drift = lambda x, t: 0.02 * x
    diffusion = lambda x, t: 0.3 * x

    ou_k = 2.0
    ou_theta = 0.25
    ou_eta = 0.08

    ou_drift = lambda x, t: ou_k * (ou_theta - x)
    ou_diffusion = lambda x, t: ou_eta * x

    sim_asset_paths = euler(drift, diffusion, 100.0, 1.0, num_days, 10)
    sim_spread_paths = euler(ou_drift, ou_diffusion, 0.1, 1.0, num_days, 10)
    asset_x = sim_asset_paths[1, :]
    spread = sim_spread_paths[1, :]
    asset_y = np.exp(np.log(asset_x) + spread)

    asset_x_df = pd.DataFrame({"dates": dates,
                               "Open": asset_x,
                               "High": asset_x,
                               "Low": asset_x,
                               "Close": asset_x,
                               "Volume": 10000 * np.ones(num_days)})

    asset_y_df = pd.DataFrame({"dates": dates,
                               "Open": asset_y,
                               "High": asset_y,
                               "Low": asset_y,
                               "Close": asset_y,
                               "Volume": 10000 * np.ones(num_days)})

    asset_x_df = asset_x_df.set_index(keys="dates")
    asset_y_df = asset_y_df.set_index(keys="dates")

    dict_df = {'XXX': asset_x_df,
               'YYY': asset_y_df}

    feed = PandasMemoryDataFeed(dict_df, ref_data_mgr=mgr)
    broker = Simulator()

    config = BacktestingConfig(stg_id="pairou", portfolio_id='test',
                               instrument_ids=[0, 1],
                               subscription_types=[BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                               from_date=dates[0], to_date=dates[-1],
                               broker_id=Simulator.ID,
                               feed_id=PandasMemoryDataFeed.ID)

    ou_params = {"k": ou_k,
                 "theta": ou_theta,
                 "eta": ou_eta}

    strategy = PairTradingWithOUSpread("pairou",
                                       ou_params=ou_params,
                                       gamma=1.0,
                                       trading_config=config,
                                       ref_data_mgr=mgr)

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

    # import matplotlib.pyplot as plt
    # plt.show()


if __name__ == "__main__":
    main()
