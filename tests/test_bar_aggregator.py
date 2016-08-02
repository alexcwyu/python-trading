from unittest import TestCase

from algotrader.event.market_data import Trade, Bar, Quote
from algotrader.trading.bar_aggregator import BarAggregator, BarInputType, BarType
from algotrader.utils.clock import simluation_clock
from algotrader.utils.time_series import DataSeries


class BarAggregatorTest(TestCase):
    class DummyEventBus:
        def __init__(self):
            self.items = []

        def reset(self):
            self.items = []

        def on_next(self, item):
            print item
            self.items.append(item)

    def setUp(self):
        simluation_clock.reset()
        self.input = DataSeries()
        self.event_bus = BarAggregatorTest.DummyEventBus()
        self.time = 9000000000
        simluation_clock.update_time(self.time)


    @classmethod
    def tearDownClass(cls):
        simluation_clock.reset()

    def update(self, input, data):
        simluation_clock.update_time(data.timestamp)
        self.input.add(data.to_dict())

    def test_time_bar_from_trade(self):
        agg = BarAggregator(data_bus=self.event_bus, clock=simluation_clock, inst_id=1, input=self.input)
        agg.start()
        self.assertEqual(0, len(self.event_bus.items))

        self.time += 10000
        t = Trade(timestamp=self.time, inst_id=1, price=20, size=200)
        self.update(self.input, t)
        self.assertEqual(1, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        # expect get a aggregated bar at 9000059999
        self.time += 49999
        t = Trade(timestamp=self.time, inst_id=1, price=10, size=200)
        self.update(self.input, t)

        items = self.event_bus.items
        self.assertEqual(1, len(items))
        self.assertEqual(0, agg.count())
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000000000, timestamp=9000059999, type=1, size=60, open=20, high=20, low=10,
                close=10, vol=400, adj_close=0), items[0])

    def test_time_bar_from_bid(self):
        agg = BarAggregator(data_bus=self.event_bus, clock=simluation_clock, inst_id=1, input=self.input,
                            input_type=BarInputType.Bid)
        agg.start()
        self.assertEqual(0, len(self.event_bus.items))

        self.time += 10000
        t = Quote(timestamp=self.time, inst_id=1, bid=30, bid_size=100)
        self.update(self.input, t)
        self.assertEqual(1, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 10000
        t = Quote(timestamp=self.time, inst_id=1, bid=10, bid_size=200)
        self.update(self.input, t)
        self.assertEqual(2, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 10000
        t = Quote(timestamp=self.time, inst_id=1, bid=70, bid_size=300)
        self.update(self.input, t)
        self.assertEqual(3, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 29998
        t = Quote(timestamp=self.time, inst_id=1, bid=50, bid_size=400)
        self.update(self.input, t)
        self.assertEqual(4, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 3
        simluation_clock.update_time(self.time)
        items = self.event_bus.items
        self.assertEqual(1, len(items))
        self.assertEqual(0, agg.count())
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000000000, timestamp=9000059999, type=1, size=60, open=30, high=70, low=10,
                close=50, vol=1000, adj_close=0), items[0])

    def test_time_bar_from_ask(self):
        agg = BarAggregator(data_bus=self.event_bus, clock=simluation_clock, inst_id=1, input=self.input,
                            input_type=BarInputType.Ask)
        agg.start()
        self.assertEqual(0, len(self.event_bus.items))

        self.time += 10000
        t = Quote(timestamp=self.time, inst_id=1, ask=30, ask_size=100)
        self.update(self.input, t)
        self.assertEqual(1, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 60000
        t = Quote(timestamp=self.time, inst_id=1, ask=70, ask_size=300)
        self.update(self.input, t)
        items = self.event_bus.items
        self.assertEqual(1, len(items))
        self.assertEqual(1, agg.count())
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000000000, timestamp=9000059999, type=1, size=60, open=30, high=30, low=30,
                close=30, vol=100, adj_close=0), items[0])

        self.event_bus.reset()

        self.time += 49999
        t = Quote(timestamp=self.time, inst_id=1, ask=20, ask_size=100)
        self.update(self.input, t)
        items = self.event_bus.items
        self.assertEqual(1, len(items))
        self.assertEqual(0, agg.count())
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000060000, timestamp=9000119999, type=1, size=60, open=70, high=70, low=20,
                close=20, vol=400, adj_close=0), items[0])


    def test_time_bar_from_bidask(self):
        agg = BarAggregator(data_bus=self.event_bus, clock=simluation_clock, inst_id=1, input=self.input,
                            input_type=BarInputType.BidAsk)
        agg.start()
        self.assertEqual(0, len(self.event_bus.items))

        self.time += 10000
        t = Quote(timestamp=self.time, inst_id=1, ask=30, ask_size=100, bid=0, bid_size=200)
        self.update(self.input, t)
        self.assertEqual(1, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 10000
        t = Quote(timestamp=self.time, inst_id=1, ask=20, ask_size=150, bid=10, bid_size=0)
        self.update(self.input, t)
        self.assertEqual(2, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 39999
        t = Quote(timestamp=self.time, inst_id=1, ask=70, ask_size=300, bid=80, bid_size=10)
        self.update(self.input, t)
        items = self.event_bus.items
        self.assertEqual(1, len(items))
        self.assertEqual(0, agg.count())
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000000000, timestamp=9000059999, type=1, size=60, open=30, high=80, low=20,
                close=80, vol=260, adj_close=0), items[0])


    def test_time_bar_from_mid(self):
        agg = BarAggregator(data_bus=self.event_bus, clock=simluation_clock, inst_id=1, input=self.input,
                            input_type=BarInputType.Middle)
        agg.start()
        self.assertEqual(0, len(self.event_bus.items))

        self.time += 59999
        t = Quote(timestamp=self.time, inst_id=1, ask=30, ask_size=100, bid=18, bid_size=200)
        self.update(self.input, t)
        items = self.event_bus.items
        self.assertEqual(1, len(items))
        self.assertEqual(0, agg.count())
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000000000, timestamp=9000059999, type=1, size=60, open=24, high=24, low=24,
                close=24, vol=150, adj_close=0), items[0])


    def test_tick_bar_from_trade(self):
        agg = BarAggregator(data_bus=self.event_bus, clock=simluation_clock, inst_id=1, input=self.input, output_bar_type=BarType.Tick, output_size=3)
        agg.start()
        self.assertEqual(0, len(self.event_bus.items))

        self.time += 60000
        t = Trade(timestamp=self.time, inst_id=1, price=20, size=200)
        self.update(self.input, t)
        self.assertEqual(1, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 60000
        t = Trade(timestamp=self.time, inst_id=1, price=80, size=100)
        self.update(self.input, t)
        self.assertEqual(2, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 60000
        t = Trade(timestamp=self.time, inst_id=1, price=10, size=200)
        self.update(self.input, t)

        items = self.event_bus.items
        self.assertEqual(1, len(items))
        self.assertEqual(0, agg.count())
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000060000, timestamp=9000180000, type=BarType.Tick, size=3, open=20, high=80, low=10,
                close=10, vol=500, adj_close=0), items[0])


    def test_vol_bar_from_trade(self):
        agg = BarAggregator(data_bus=self.event_bus, clock=simluation_clock, inst_id=1, input=self.input, output_bar_type=BarType.Volume, output_size=1000)
        agg.start()
        self.assertEqual(0, len(self.event_bus.items))

        self.time += 60000
        t = Trade(timestamp=self.time, inst_id=1, price=20, size=200)
        self.update(self.input, t)
        self.assertEqual(1, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 60000
        t = Trade(timestamp=self.time, inst_id=1, price=80, size=100)
        self.update(self.input, t)
        self.assertEqual(2, agg.count())
        self.assertTrue(len(self.event_bus.items) == 0)

        self.time += 60000
        t = Trade(timestamp=self.time, inst_id=1, price=10, size=1000)
        self.update(self.input, t)

        items = self.event_bus.items
        self.assertEqual(1, len(items))
        self.assertEqual(1, agg.count())
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000060000, timestamp=9000180000, type=BarType.Volume, size=1000, open=20, high=80, low=10,
                close=10, vol=1000, adj_close=0), items[0])

        self.event_bus.reset()

        self.time += 60000
        t = Trade(timestamp=self.time, inst_id=1, price=50, size=2800)
        self.update(self.input, t)

        items = self.event_bus.items
        self.assertEqual(3, len(items))
        self.assertEqual(1, agg.count())
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000180000, timestamp=9000240000, type=BarType.Volume, size=1000, open=10, high=50, low=10,
                close=50, vol=1000, adj_close=0), items[0])
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000240000, timestamp=9000240000, type=BarType.Volume, size=1000, open=50, high=50, low=50,
                close=50, vol=1000, adj_close=0), items[1])
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000240000, timestamp=9000240000, type=BarType.Volume, size=1000, open=50, high=50, low=50,
                close=50, vol=1000, adj_close=0), items[2])


        self.event_bus.reset()

        self.time += 60000
        t = Trade(timestamp=self.time, inst_id=1, price=20, size=900)
        self.update(self.input, t)

        items = self.event_bus.items
        self.assertEqual(1, len(items))
        self.assertEqual(0, agg.count())
        self.assertEqual(
            Bar(inst_id=1, begin_time=9000240000, timestamp=9000300000, type=BarType.Volume, size=1000, open=50, high=50, low=20,
                close=20, vol=1000, adj_close=0), items[0])
