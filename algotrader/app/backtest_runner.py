

from datetime import date

from algotrader.app import Application
from algotrader.chart.plotter import StrategyPlotter
from algotrader.config.app import ApplicationConfig
from algotrader.config.persistence import PersistenceConfig
from algotrader.config.trading import BacktestingConfig
from algotrader.event.market_data import BarSize, BarType
from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock
from algotrader.provider.broker import Broker


class BacktestRunner(Application):
    def init(self):
        self.app_context.start()
        self.trading_config = self.app_config.get_trading_configs()[0]
        self.portfolio = self.app_context.portf_mgr.get_or_new_portfolio(self.trading_config.portfolio_id,
                                                                         self.trading_config.portfolio_initial_cash)

        self.initial_result = self.portfolio.get_result()

        self.app_context.add_startable(self.portfolio)

        self.strategy = self.app_context.stg_mgr.get_or_new_stg(self.trading_config)
        self.app_context.add_startable(self.strategy)

    def run(self):
        self.strategy.start(self.app_context)
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
        plotter.plot(instrument=4)


def main():
    backtest_config = BacktestingConfig(id="down2%-test-config", stg_id="down2%",
                                        stg_cls='algotrader.strategy.down_2pct_strategy.Down2PctStrategy',
                                        portfolio_id='test', portfolio_initial_cash=100000,
                                        instrument_ids=[4],
                                        subscription_types=[
                                            BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                                        from_date=date(2010, 1, 1), to_date=date.today(),
                                        broker_id=Broker.Simulator,
                                        feed_id=Feed.CSV,
                                        stg_configs={'qty': 1000})
    app_config = ApplicationConfig("down2%", RefDataManager.InMemory, Clock.Simulation, PersistenceConfig(),
                                   backtest_config)
    app_context = ApplicationContext(app_config=app_config)

    BacktestRunner().start(app_context)


if __name__ == "__main__":
    main()
