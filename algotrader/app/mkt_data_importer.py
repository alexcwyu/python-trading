from gevent import monkey

monkey.patch_all()
from algotrader.provider.subscription import MarketDataSubscriber
from algotrader.app import Application
from algotrader.utils.logging import logger
import time
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext


class MktDataImporter(Application, MarketDataSubscriber):
    def init(self):
        self.app_config = self.app_context.app_config

    def run(self):
        logger.info("importing data")

        self.app_context.start()

        self.feed = self.app_context.provider_mgr.get(self.app_config.get_app_config("feedId"))
        self.feed.start(self.app_context)
        self.instruments = self.ref_data_mgr.get_insts_by_ids(self.app_config.get_app_config("instrumentIds"))
        self.subscript_market_data(self.feed, self.instruments,
                                   self.app_config.get_app_config("subscriptionTypes"),
                                   self.app_config.get_app_config("fromDate"),
                                   self.app_config.get_app_config("toDate"))

        logger.info("ATS started, presss Ctrl-C to stop")
        for i in range(1, 1000):
            time.sleep(1)
            logger.info(".")


def main():
    app_config = Config(load_from_yaml("../../config/data_import.yaml"),
                        {"Application": {"feedId": "Yahoo"}})
    app_context = ApplicationContext(app_config=app_config)
    MktDataImporter().start(app_context)


if __name__ == "__main__":
    main()
