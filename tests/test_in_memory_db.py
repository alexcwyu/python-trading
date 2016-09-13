import random
from unittest import TestCase

from algotrader.event.market_data import Bar
from algotrader.provider.persistence.inmemory import InMemoryDataStore


class InMemoryDBTest(TestCase):
    def setUp(self):
        self.db = InMemoryDataStore()
        self.db.start()

    def tearDown(self):
        self.db.delete_db()

    def test_save_and_load(self):
        inputs = []
        for x in range(0, 10):
            data = sorted([random.randint(0, 100) for i in range(0, 4)])
            bar = Bar(timestamp=x, inst_id=3, open=data[1], high=data[3], low=data[0], close=data[2],
                      vol=random.randint(100, 1000))
            inputs.append(bar)
            self.db.save_bar(bar)

        self.db.stop()

        self.db = InMemoryDataStore()
        self.db.start(None)

        bars = self.db.load_all('bars')
        bars = sorted(bars, cmp=lambda x, y: x.timestamp - y.timestamp, reverse=False)
        self.assertEquals(10, len(bars))

        for x in range(0, 10):
            self.assertEquals(inputs[x], bars[x])


