import datetime
import time
import unittest
from unittest import TestCase

import gevent
from nose.tools import nottest

from algotrader.model.model_factory import ModelFactory
from algotrader.trading.clock import SimulationClock, RealTimeClock
from algotrader.utils.date import datetime_to_unixtimemillis, unixtimemillis_to_datetime


class ClockTest(TestCase):
    ts = 1467870720000

    def sim_action(self, *arg):
        self.endtime.append(self.simluation_clock.now())

    def realtime_action(self, *arg):
        self.endtime.append(self.realtime_clock.now())

    def setUp(self):
        self.simluation_clock = SimulationClock()
        self.realtime_clock = RealTimeClock()
        self.simluation_clock.reset()
        self.endtime = []
        self.simluation_clock.update_time(ClockTest.ts)

    def test_simulation_clock_current_date_time_with_bar(self):
        timestamp = ClockTest.ts + 10
        bar = ModelFactory.build_bar(inst_id="test", timestamp=timestamp)
        self.simluation_clock.on_bar(bar)
        self.assertEquals(timestamp, self.simluation_clock.now())

    def test_simulation_clock_current_date_time_with_quote(self):
        timestamp = ClockTest.ts + 10
        quote = ModelFactory.build_quote(inst_id="test", timestamp=timestamp)
        self.simluation_clock.on_quote(quote)
        self.assertEquals(timestamp, self.simluation_clock.now())

    def test_simulation_clock_current_date_time_with_trade(self):
        timestamp = ClockTest.ts + 10
        trade = ModelFactory.build_trade(inst_id="test", timestamp=timestamp)
        self.simluation_clock.on_trade(trade)
        self.assertEquals(timestamp, self.simluation_clock.now())

    def test_simulation_clock_now(self):
        self.assertEquals(ClockTest.ts, self.simluation_clock.now())

    def test_simulation_clock_reset(self):
        self.simluation_clock.reset()
        self.assertEquals(0, self.simluation_clock.now())

    def test_simulation_clock_schedule_absolute(self):
        self.simluation_clock.schedule_absolute(ClockTest.ts + 1000, self.sim_action)

        self.assertEquals([], self.endtime)

        self.simluation_clock.update_time(ClockTest.ts + 999)
        self.assertEquals([], self.endtime)

        self.simluation_clock.update_time(ClockTest.ts + 1000)
        self.assertEquals([ClockTest.ts + 1000], self.endtime)

        self.simluation_clock.update_time(ClockTest.ts + 1001)
        self.assertEquals([ClockTest.ts + 1000], self.endtime)

    def test_simulation_schedule_absolute_beyond_trigger_time(self):
        self.simluation_clock.schedule_absolute(ClockTest.ts + 1000, self.sim_action)

        self.assertEquals([], self.endtime)

        self.simluation_clock.update_time(ClockTest.ts + 5000)
        self.assertEquals([ClockTest.ts + 5000], self.endtime)

    def test_simulation_schedule_relative(self):
        self.simluation_clock.schedule_relative(datetime.timedelta(seconds=3), self.sim_action)

        self.assertEquals([], self.endtime)

        self.simluation_clock.update_time(ClockTest.ts + 1000)
        self.assertEquals([], self.endtime)

        self.simluation_clock.update_time(ClockTest.ts + 3000)
        self.assertEquals([ClockTest.ts + 3000], self.endtime)

        self.simluation_clock.update_time(ClockTest.ts + 4000)
        self.assertEquals([ClockTest.ts + 3000], self.endtime)

    def test_simulation_schedule_relative_beyond_trigger_time(self):
        self.simluation_clock.schedule_relative(3000, self.sim_action, )

        self.assertEquals([], self.endtime)

        self.simluation_clock.update_time(ClockTest.ts + 5000)
        self.assertEquals([ClockTest.ts + 5000], self.endtime)

    @nottest
    def test_timestamp_conversion(self):
        # dt = datetime.datetime(year=2000, month=1, day=1, hour=7, minute=30, second=30)
        dt = datetime.datetime(year=1999, month=12, day=31, hour=23, minute=30, second=30)
        ts = datetime_to_unixtimemillis(dt)
        self.assertEqual(946683030000, ts)

        dt2 = unixtimemillis_to_datetime(ts)
        self.assertEqual(dt, dt2)

        dt3 = datetime.datetime.fromtimestamp(0)

        ts2 = datetime_to_unixtimemillis(dt3)
        dt4 = unixtimemillis_to_datetime(ts2)
        self.assertEquals(28800000, ts2)
        self.assertEquals(dt3, dt4)

    def test_real_time_clock_now(self):
        ts = datetime_to_unixtimemillis(datetime.datetime.now())
        ts2 = self.realtime_clock.now()
        self.assertTrue(abs(ts - ts2) <= 10)
        time.sleep(2)
        ts3 = self.realtime_clock.now()
        self.assertAlmostEqual(ts3 - ts2, 2000, -2)

    @unittest.skip("fix abs scheduling later")
    def test_real_time_clock_schedule_absolute(self):
        start = self.realtime_clock.now()
        dt = unixtimemillis_to_datetime(start)
        abs_time = dt + datetime.timedelta(seconds=1)
        self.realtime_clock.schedule_absolute(abs_time, self.realtime_action)
        self.assertEquals([], self.endtime)
        time.sleep(3)
        self.assertEquals(1, len(self.endtime))
        self.assertAlmostEqual(1000, self.endtime[0] - start, -2)

    def test_real_time_clock_schedule_relative(self):
        start = self.realtime_clock.now()
        self.realtime_clock.schedule_relative(datetime.timedelta(seconds=1), self.realtime_action)
        self.assertEqual([], self.endtime)
        time.sleep(1.1)
        self.assertEqual(1, len(self.endtime))
        self.assertAlmostEqual(1000, self.endtime[0] - start, -2)

    def test_real_time_clock_now(self):
        s1 = gevent.core.time()
        s2 = datetime.datetime.fromtimestamp(s1)
        s3 = self.realtime_clock.now()
        s4 = unixtimemillis_to_datetime(s3)

        self.assertAlmostEqual(s1 * 1000, s3, -2)
