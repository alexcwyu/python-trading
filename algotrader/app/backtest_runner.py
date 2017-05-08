from algotrader.app import Application

from algotrader.chart.plotter import StrategyPlotter
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from algotrader.utils.logging import logger


class BacktestRunner(Application):
    def init(self):
        self.config = self.app_context.config

        self.is_plot = self.config.get_app_config("plot", default=True)

    def run(self):
        logger.info("starting BackTest")

        self.app_context.start()
        self.portfolio = self.app_context.portf_mgr.get_or_new_portfolio(self.config.get_app_config("portfolioId"),
                                                                         self.config.get_app_config(
                                                                             "portfolioInitialcash"))
        self.strategy = self.app_context.stg_mgr.get_or_new_stg(self.config.get_app_config("stgId"),
                                                                self.config.get_app_config("stgCls"))

        self.initial_result = self.portfolio.get_result()
        self.app_context.add_startable(self.portfolio)
        self.portfolio.start(self.app_context)
        self.strategy.start(self.app_context)

        result = self.portfolio.get_result()
        print("Initial:", self.initial_result)
        print("Final:", result)
        if self.is_plot:
            self.plot()

    def plot(self):
        # pyfolio
        ret = self.portfolio.get_return()
        # import pyfolio as pf
        # pf.create_returns_tear_sheet(ret)
        # pf.create_full_tear_sheet(ret)

        # build in plot

        plotter = StrategyPlotter(self.strategy)
        plotter.plot(instrument=self.app_context.config.get_app_config("instrumentIds")[0])


def main():
    config = Config(
        load_from_yaml("../../config/backtest.yaml"),
        load_from_yaml("../../config/down2%.yaml"))

    app_context = ApplicationContext(config=config)

    BacktestRunner().start(app_context)


if __name__ == "__main__":
    main()
