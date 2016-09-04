import datetime
import time
from unittest import TestCase

import gevent

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.utils.clock import simluation_clock, realtime_clock
from algotrader.utils.date_utils import DateUtils


class ClockTest(TestCase):
    endtime = []
    ts = 1467870720000

    @staticmethod
    def simclock_action(*arg):
        ClockTest.endtime.append(simluation_clock.now())

    @staticmethod
    def realtime_action(*arg):
        ClockTest.endtime.append(realtime_clock.now())

    @classmethod
    def tearDownClass(cls):
        simluation_clock.reset()

    def setUp(self):
        simluation_clock.reset()
        ClockTest.endtime = []
        simluation_clock.update_time(ClockTest.ts)

    def test_simulation_clock_current_date_time_with_bar(self):
        timestamp = ClockTest.ts + 10
        bar = Bar(timestamp=timestamp)
        simluation_clock.on_bar(bar)
        self.assertEquals(timestamp, simluation_clock.now())

    def test_simulation_clock_current_date_time_with_quote(self):
        timestamp = ClockTest.ts + 10
        quote = Quote(timestamp=timestamp)
        simluation_clock.on_quote(quote)
        self.assertEquals(timestamp, simluation_clock.now())

    def test_simulation_clock_current_date_time_with_trade(self):
        timestamp = ClockTest.ts + 10
        trade = Trade(timestamp=timestamp)
        simluation_clock.on_trade(trade)
        self.assertEquals(timestamp, simluation_clock.now())

    def test_simulation_clock_now(self):
        self.assertEquals(ClockTest.ts, simluation_clock.now())

    def test_simulation_clock_reset(self):
        simluation_clock.reset()
        self.assertEquals(0, simluation_clock.now())

    def test_simulation_clock_schedule_absolute(self):
        simluation_clock.schedule_absolute(ClockTest.ts + 1000, ClockTest.simclock_action)

        self.assertEquals([], ClockTest.endtime)

        simluation_clock.update_time(ClockTest.ts + 999)
        self.assertEquals([], ClockTest.endtime)

        simluation_clock.update_time(ClockTest.ts + 1000)
        self.assertEquals([ClockTest.ts + 1000], ClockTest.endtime)

        simluation_clock.update_time(ClockTest.ts + 1001)
        self.assertEquals([ClockTest.ts + 1000], ClockTest.endtime)

    def test_simulation_schedule_absolute_beyond_trigger_time(self):
        simluation_clock.schedule_absolute(ClockTest.ts + 1000, ClockTest.simclock_action)

        self.assertEquals([], ClockTest.endtime)

        simluation_clock.update_time(ClockTest.ts + 5000)
        self.assertEquals([ClockTest.ts + 5000], ClockTest.endtime)

    def test_simulation_schedule_relative(self):
        simluation_clock.schedule_relative(datetime.timedelta(seconds=3), ClockTest.simclock_action)

        self.assertEquals([], ClockTest.endtime)

        simluation_clock.update_time(ClockTest.ts + 1000)
        self.assertEquals([], ClockTest.endtime)

        simluation_clock.update_time(ClockTest.ts + 3000)
        self.assertEquals([ClockTest.ts + 3000], ClockTest.endtime)

        simluation_clock.update_time(ClockTest.ts + 4000)
        self.assertEquals([ClockTest.ts + 3000], ClockTest.endtime)

    def test_simulation_schedule_relative_beyond_trigger_time(self):
        simluation_clock.schedule_relative(3000, ClockTest.simclock_action)

        self.assertEquals([], ClockTest.endtime)

        simluation_clock.update_time(ClockTest.ts + 5000)
        self.assertEquals([ClockTest.ts + 5000], ClockTest.endtime)

    def test_timestamp_conversion(self):
        dt = datetime.datetime(year=2000, month=1, day=1, hour=7, minute=30, second=30)
        ts = DateUtils.datetime_to_unixtimemillis(dt)
        self.assertEqual(946683030000, ts)

        dt2 = DateUtils.unixtimemillis_to_datetime(ts)
        self.assertEquals(dt, dt2)

        dt3 = datetime.datetime.fromtimestamp(0)

        ts2 = DateUtils.datetime_to_unixtimemillis(dt3)
        dt4 = DateUtils.unixtimemillis_to_datetime(ts2)
        self.assertEquals(0, ts2)
        self.assertEquals(dt3, dt4)

    def test_real_time_clock_now(self):
        ts = DateUtils.datetime_to_unixtimemillis(datetime.datetime.now())
        ts2 = realtime_clock.now()
        self.assertTrue(abs(ts - ts2) <= 10)
        time.sleep(2)
        ts3 = realtime_clock.now()
        self.assertAlmostEqual(ts3 - ts2, 2000, -2)

    def test_real_time_clock_schedule_absolute(self):
        start = realtime_clock.now()
        dt = DateUtils.unixtimemillis_to_datetime(start)
        abs_time = dt + datetime.timedelta(seconds=1)
        realtime_clock.schedule_absolute(abs_time, ClockTest.realtime_action)
        self.assertEquals([], ClockTest.endtime)
        time.sleep(1.1)
        self.assertEquals(1, len(ClockTest.endtime))
        self.assertAlmostEqual(1000, ClockTest.endtime[0] - start, -2)

    def test_real_time_clock_schedule_relative(self):
        start = realtime_clock.now()
        print start
        print DateUtils.unixtimemillis_to_datetime(start)
        realtime_clock.schedule_relative(datetime.timedelta(seconds=1), ClockTest.realtime_action)
        self.assertEquals([], ClockTest.endtime)
        time.sleep(1.1)
        self.assertEquals(1, len(ClockTest.endtime))
        self.assertAlmostEqual(1000, ClockTest.endtime[0] - start, -2)

    def test_real_time_clock_now(self):
        s1 = gevent.core.time()
        s2 = datetime.datetime.fromtimestamp(s1)
        print s1, s2
        s3 = realtime_clock.now()
        s4 = DateUtils.unixtimemillis_to_datetime(s3)
        print s3, s4

        self.assertAlmostEqual(s1 * 1000, s3, -2)
