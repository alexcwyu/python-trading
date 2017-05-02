from gevent import monkey

monkey.patch_all()
from algotrader.provider.subscription import MarketDataSubscriber
from algotrader.app import Application
from algotrader.provider.broker import Broker
from algotrader.provider.persistence import PersistenceMode
from algotrader.provider.persistence.data_store import DataStore
from algotrader.utils.market_data_utils import BarSize
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils import logger
from algotrader.trading.clock import Clock
import time
from algotrader.model.market_data_pb2 import Bar


class MktDataImporter(Application, MarketDataSubscriber):
    def init(self):
        logger.info("importing data")

        self.app_context.start()

        self.app_config = self.app_context.app_config
        self.feed = self.app_context.provider_mgr.get(self.app_config.feed_id)
        self.feed.start(self.app_context)

    def run(self):
        self.instruments = self.app_context.ref_data_mgr.get_insts(self.app_config.instrument_ids)
        self.subscript_market_data(self.feed, self.instruments, self.app_config.subscription_types,
                                       self.app_config.from_date, self.app_config.to_date)

        logger.info("ATS started, presss Ctrl-C to stop")
        for i in range(1, 1000):
            time.sleep(1)
            logger.info(".")


def main():
    pass
    # persistence_config = PersistenceConfig(None,
    #                                        DataStore.Mongo, PersistenceMode.RealTime,
    #                                        DataStore.Mongo, PersistenceMode.RealTime,
    #                                        DataStore.Mongo, PersistenceMode.RealTime,
    #                                        DataStore.Mongo, PersistenceMode.RealTime)
    # app_config = RealtimeMarketDataImporterConfig(None, feed_id=Broker.IB, instrument_ids=[3],
    #                                               subscription_types=[
    #                                                   BarSubscriptionType(bar_type=Bar.Time, bar_size=BarSize.D1)],
    #                                               ref_data_mgr_type=RefDataManager.InMemory, clock_type=Clock.RealTime,
    #                                               persistence_config=persistence_config,
    #                                               provider_configs=[MongoDBConfig(), IBConfig(client_id=2)])
    # app_context = ApplicationContext(app_config=app_config)
    #
    # MktDataImporter().start(app_context)


if __name__ == "__main__":
    main()
