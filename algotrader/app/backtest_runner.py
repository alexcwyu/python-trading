from datetime import date

from algotrader.app import Application
from algotrader.chart.plotter import StrategyPlotter
from algotrader.config.app import BacktestingConfig
from algotrader.config.builder import *
from algotrader.config.feed import CSVFeedConfig
from algotrader.model.market_data_pb2 import Bar
from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.market_data_utils import BarSize


class BacktestRunner(Application):
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
        print
        self.portfolio.get_result()

        # pyfolio
        rets = self.portfolio.get_return()
        # import pyfolio as pf
        # pf.create_returns_tear_sheet(rets)
        # pf.create_full_tear_sheet(rets)

        # build in plot
        plotter = StrategyPlotter(self.strategy)
        plotter.plot(instrument=self.app_context.app_config.instrument_ids[0])


def main():
    backtest_config = BacktestingConfig(id="down2%-test-config", stg_id="down2%",
                                        stg_cls='algotrader.strategy.down_2pct_strategy.Down2PctStrategy',
                                        portfolio_id='test', portfolio_initial_cash=100000,
                                        instrument_ids=[1],
                                        subscription_types=[
                                            BarSubscriptionType(bar_type=Bar.Time, bar_size=BarSize.D1)],
                                        from_date=date(2010, 1, 1), to_date=date.today(),
                                        broker_id=Broker.Simulator,
                                        feed_id=Feed.CSV,
                                        stg_configs={'qty': 1000},
                                        ref_data_mgr_type=RefDataManager.DB,
                                        persistence_config=backtest_mongo_persistance_config(),
                                        provider_configs=[MongoDBConfig(), CSVFeedConfig(path='../../data/tradedata')])
    app_context = ApplicationContext(app_config=backtest_config)

    BacktestRunner(True).start(app_context)


if __name__ == "__main__":
    main()
