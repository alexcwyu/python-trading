from datetime import date

from algotrader.chart.plotter import StrategyPlotter
from algotrader.config.app import ApplicationConfig
from algotrader.config.trading import BacktestingConfig
from algotrader.event.market_data import BarSize, BarType
from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock


class BacktestRunner(object):
    def __init__(self, backtest_config):
        self.backtest_config = backtest_config

    def start(self):
        self.app_config = ApplicationConfig(None, None, None, None, None, RefDataManager.InMemory, Clock.Simulation,
                                            self.backtest_config)
        self.app_context = ApplicationContext(app_config=self.app_config)
        self.app_context.start()

        self.portfolio = self.app_context.portf_mgr.new_portfolio(self.backtest_config.portfolio_id,
                                                                  self.backtest_config.portfolio_initial_cash)
        self.app_context.add_startable(self.portfolio)


        self.strategy = self.app_context.stg_mgr.new_stg(self.backtest_config)
        self.app_context.add_startable(self.strategy)

        self.strategy.start(self.app_context)


    def stop(self):
        self.app_context.stop()

    def plot(self):
        print self.portfolio.get_result()

        # pyfolio
        rets = self.portfolio.get_return()
        # import pyfolio as pf
        # pf.create_returns_tear_sheet(rets)
        # pf.create_full_tear_sheet(rets)

        # build in plot
        plotter = StrategyPlotter(self.strategy)
        plotter.plot(instrument=4)


def main():
    config = BacktestingConfig(stg_id="down2%", stg_cls='algotrader.strategy.down_2pct_strategy.Down2PctStrategy',
                               portfolio_id='test', portfolio_initial_cash=100000,
                               instrument_ids=[4],
                               subscription_types=[BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                               from_date=date(2010, 1, 1), to_date=date.today(),
                               broker_id=Broker.Simulator,
                               feed_id=Feed.CSV,
                               stg_configs={'qty': 1000})

    runner = BacktestRunner(config)
    try:
        runner.start()
        # portfolio = runner.portfolio
        # strategy = runner.strategy
        # print portfolio.get_result()
        #
        # # pyfolio
        # rets = portfolio.get_return()
        # # import pyfolio as pf
        # # pf.create_returns_tear_sheet(rets)
        # # pf.create_full_tear_sheet(rets)
        #
        # # build in plot
        # plotter = StrategyPlotter(strategy)
        # plotter.plot(instrument=4)
        #
        # # import matplotlib.pyplot as plt
        # # plt.show()
        runner.plot()
    finally:
        runner.stop()


if __name__ == "__main__":
    main()
