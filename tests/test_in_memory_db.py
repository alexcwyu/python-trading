import random

from algotrader.config.app import ApplicationConfig
from algotrader.config.persistence import PersistenceConfig, InMemoryStoreConfig
from algotrader.provider.persistence import PersistenceMode
from unittest import TestCase

from algotrader.model.model_factory import ModelFactory
from algotrader.provider.persistence import DataStore
from algotrader.provider.persistence.inmemory import InMemoryDataStore
from algotrader.trading.clock import Clock
from algotrader.trading.context import ApplicationContext


class InMemoryDBTest(TestCase):
    def setUp(self):

        persistence_config = PersistenceConfig(None,
                                               DataStore.InMemory, PersistenceMode.Batch,
                                               DataStore.InMemory, PersistenceMode.Batch,
                                               DataStore.InMemory, PersistenceMode.Batch,
                                               DataStore.InMemory, PersistenceMode.Batch)

        name = "test"
        create_at_start = True
        delete_at_stop = False

        app_config = ApplicationConfig(None, None, Clock.RealTime, persistence_config,
                                       InMemoryStoreConfig(file="%s_db.p" % name,
                                                           create_at_start=create_at_start,
                                                           delete_at_stop=delete_at_stop))
        self.context = ApplicationContext(app_config=app_config)

        self.db = InMemoryDataStore()
        self.db.start(self.context)

    def tearDown(self):
        self.db.remove_database()

    def test_save_and_load(self):
        inputs = []
        for x in range(0, 10):
            data = sorted([random.randint(0, 100) for i in range(0, 4)])
            bar = ModelFactory.build_bar(timestamp=x, inst_id="3", open=data[1], high=data[3], low=data[0],
                                         close=data[2],
                                         vol=random.randint(100, 1000))
            inputs.append(bar)
            self.db.save_bar(bar)

        self.db.stop()

        self.db = InMemoryDataStore()
        self.db.start(self.context)

        bars = self.db.load_all('bars')
        bars = sorted(bars, key=lambda x: x.timestamp, reverse=False)
        self.assertEquals(10, len(bars))

        for x in range(0, 10):
            self.assertEquals(inputs[x], bars[x])
