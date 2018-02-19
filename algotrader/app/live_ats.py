from algotrader.app import Application
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from algotrader.utils.logging import logger


class ATSRunner(Application):
    def init(self):
        self.config = self.app_context.config

        self.portfolio = self.app_context.portf_mgr.get_or_new_portfolio(self.config.get_app_config("portfolioId"),
                                                                         self.config.get_app_config(
                                                                             "portfolioInitialcash"))
        self.app_context.add_startable(self.portfolio)

        self.strategy = self.app_context.stg_mgr.get_or_new_stg(self.config.get_app_config("stgId"),
                                                                self.config.get_app_config("stgCls"))
        self.app_context.add_startable(self.strategy)

    def run(self):
        logger.info("starting ATS")

        self.app_context.start()
        self.strategy.start(self.app_context)

        logger.info("ATS started, presss Ctrl-C to stop")


def main():
    config = Config(
        load_from_yaml("../../config/live_ib.yaml"),
        load_from_yaml("../../config/mvg_avg_force.yaml"))
        # load_from_yaml("../../config/down2%.yaml"))

    app_context = ApplicationContext(config=config)

    ATSRunner().start(app_context)


if __name__ == "__main__":
    main()
