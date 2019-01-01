from gevent import monkey

monkey.patch_all()
from algotrader.trading.subscription import MarketDataSubscriber
from algotrader.app import Application
from algotrader.utils.logging import logger
import time
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from algotrader.utils.market_data import build_subscription_requests


class MktDataImporter(Application, MarketDataSubscriber):
    def run(self):
        logger.info("importing data")
        self.app_context.start()
        config = self.app_context.config

        feed = self.app_context.provider_mgr.get(config.get_app_config("feedId"))
        feed.start(self.app_context)
        instruments = self.app_context.ref_data_mgr.get_insts_by_ids(config.get_app_config("instrumentIds"))

        for sub_req in build_subscription_requests(feed.id(), instruments,
                                                   config.get_app_config("subscriptionTypes"),
                                                   config.get_app_config("fromDate"),
                                                   config.get_app_config("toDate")):
            feed.subscribe_mktdata(sub_req)

        logger.info("ATS started, presss Ctrl-C to stop")
        for i in range(1, 1000):
            time.sleep(1)
            logger.info(".")


def main():
    config = Config(load_from_yaml("../../config/data_import.yaml"),
                        {"Application": {"feedId": "Yahoo"}})
    app_context = ApplicationContext(config=config)
    MktDataImporter().start(app_context)


if __name__ == "__main__":
    main()
