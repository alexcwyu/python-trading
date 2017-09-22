import random

from unittest import TestCase

from algotrader.model.model_factory import ModelFactory
from algotrader.provider.datastore.inmemory import InMemoryDataStore
from algotrader.trading.context import ApplicationContext
from tests import empty_config


class InMemoryDBTest(TestCase):
    def setUp(self):

        self.app_context = ApplicationContext(config=empty_config)
        self.app_context.start()

        self.db = InMemoryDataStore()
        self.db.start(self.app_context)

    def tearDown(self):
        self.db.remove_database()

    def test_save_and_load(self):
        inputs = []
        for x in range(0, 10):
            data = sorted([random.randint(0, 100) for i in range(0, 4)])
            bar = ModelFactory.build_bar(timestamp=x, inst_id="3", open=data[1], high=data[3], low=data[0],
                                         close=data[2],
                                         volume=random.randint(100, 1000))
            inputs.append(bar)
            self.db.save_bar(bar)

        self.db.stop()

        self.db = InMemoryDataStore()
        self.db.start(self.app_context)

        bars = self.db.load_all('bars')
        bars = sorted(bars, key=lambda x: x.timestamp, reverse=False)
        self.assertEquals(10, len(bars))

        for x in range(0, 10):
            self.assertEquals(inputs[x], bars[x])
