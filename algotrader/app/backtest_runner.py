from algotrader.app import Application

from algotrader.chart.plotter import StrategyPlotter
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from algotrader.utils.logging import logger


class BacktestRunner(Application):
    def init(self):
        self.app_config = self.app_context.app_config
        self.portfolio = self.app_context.portf_mgr.get_or_new_portfolio(self.app_config.get_app_config("portfolioId"),
                                                                         self.app_config.get_app_config(
                                                                             "portfolioInitialcash"))

        self.initial_result = self.portfolio.get_result()

        self.app_context.add_startable(self.portfolio)

        self.strategy = self.app_context.stg_mgr.get_or_new_stg(self.app_config.get_app_config("stgId"),
                                                                self.app_config.get_app_config("stgCls"))
        self.app_context.add_startable(self.strategy)

        self.is_plot = self.app_context.provider_mgr.get(self.app_config.get_app_config("plot", True))

    def run(self):
        logger.info("starting BackTest")

        self.app_context.start()
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
        plotter.plot(instrument=self.app_context.app_config.get_app_config("instrumentIds")[0])


def main():
    app_config = Config(
        load_from_yaml("../../config/backtest.yaml"),
        load_from_yaml("../../config/down2%.yaml"))

    app_context = ApplicationContext(app_config=app_config)

    BacktestRunner().start(app_context)


if __name__ == "__main__":
    main()
