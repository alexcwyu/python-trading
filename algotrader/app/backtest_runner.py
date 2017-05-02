from algotrader.app import Application

from algotrader.chart.plotter import StrategyPlotter
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext


class BacktestRunner(Application):
    def __init__(self, isplot=False):
        self.isplot = isplot

    def init(self):
        self.app_config = self.app_context.app_config
        self.portfolio = self.app_context.portf_mgr.get_or_new_portfolio(self.app_config.get_app_config("portfolioId"),
                                                                         self.app_config.get_app_config("portfolioInitialcash"))

        self.initial_result = self.portfolio.get_result()

        self.app_context.add_startable(self.portfolio)

        self.strategy = self.app_context.stg_mgr.get_or_new_stg(self.app_config.get_app_config("stgId"),
                                                                self.app_config.get_app_config("stgCls"))
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
    app_config = Config(
        load_from_yaml("../../config/backtest.yaml"),
        load_from_yaml("../../config/down2%.yaml"))

    app_context = ApplicationContext(app_config=app_config)

    BacktestRunner(True).start(app_context)


if __name__ == "__main__":
    main()
