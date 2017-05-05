from algotrader.app import Application
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from algotrader.utils import logger


class ATSRunner(Application):
    def init(self):
        self.app_config = self.app_config

        self.portfolio = self.app_context.portf_mgr.get_or_new_portfolio(self.app_config.get_app_config("portfolioId"),
                                                                         self.app_config.get_app_config(
                                                                             "portfolioInitialcash"))
        self.app_context.add_startable(self.portfolio)

        self.strategy = self.app_context.stg_mgr.get_or_new_stg(self.app_config.get_app_config("stgId"),
                                                                self.app_config.get_app_config("stgCls"))
        self.app_context.add_startable(self.strategy)

    def run(self):
        logger.info("starting ATS")

        self.app_context.start()
        self.strategy.start(self.app_context)

        logger.info("ATS started, presss Ctrl-C to stop")


def main():
    app_config = Config(
        load_from_yaml("../../config/live_ib.yaml"),
        load_from_yaml("../../config/down2%.yaml"))

    app_context = ApplicationContext(app_config=app_config)

    ATSRunner().start(app_context)


if __name__ == "__main__":
    main()
