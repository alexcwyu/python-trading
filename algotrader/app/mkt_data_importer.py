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
        app_config = self.app_context.app_config

        feed = self.app_context.provider_mgr.get(app_config.get_app_config("feedId"))
        feed.start(self.app_context)
        instruments = self.app_context.ref_data_mgr.get_insts_by_ids(app_config.get_app_config("instrumentIds"))

        for sub_req in build_subscription_requests(feed.id(), instruments,
                                                   app_config.get_app_config("subscriptionTypes"),
                                                   app_config.get_app_config("fromDate"),
                                                   app_config.get_app_config("toDate")):
            feed.subscribe_mktdata(sub_req)

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
