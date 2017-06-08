from datetime import datetime, timedelta

import gevent
from algotrader.event.market_data import Bar, BarSize
from rx.concurrency.historicalscheduler import HistoricalScheduler

from algotrader.trading.clock import RealTimeClock
from algotrader.utils.date import unixtimemillis_to_datetime, datetime_to_unixtimemillis

realtime_clock = RealTimeClock()


class HistoricalScheduler2(HistoricalScheduler):
    def __init__(self, initial_clock=None, comparer=None):
        def compare_datetimes(a, b):
            return (a > b) - (a < b)

        clock = initial_clock or datetime.fromtimestamp(0)
        comparer = comparer or compare_datetimes
        super(HistoricalScheduler2, self).__init__(clock, comparer)

    def now(self):
        return self.clock

    @staticmethod
    def add(absolute, relative):

        if isinstance(relative, int):
            return absolute + timedelta(milliseconds=relative)
        elif isinstance(relative, float):
            return absolute + timedelta(seconds=relative)

        return absolute + relative

    def to_datetime_offset(self, absolute):
        return absolute

    def to_relative(self, timespan):
        return timespan


starttime = datetime.now()
scheduler1 = HistoricalScheduler2(initial_clock=starttime)
from algotrader.trading.clock import RealTimeScheduler

scheduler2 = RealTimeScheduler()
endtime = [None]


def action(*arg):
    print(unixtimemillis_to_datetime(realtime_clock.now()))


from rx import Observable
import time


from gevent.greenlet import Greenlet


class MyNoopGreenlet(Greenlet):
    def __init__(self, seconds):
        Greenlet.__init__(self)
        self.seconds = seconds

    def _run(self):
        gevent.sleep(self.seconds)

    def __str__(self):
        return 'MyNoopGreenlet(%s)' % self.seconds


current_ts = datetime_to_unixtimemillis(starttime)
next_ts = Bar.get_next_bar_start_time(current_ts, BarSize.S5)
diff = next_ts - current_ts
# Observable.timer(int(diff), BarSize.S5 * 1000, scheduler2).subscribe(action)
# scheduler1.advance_to(starttime)
# scheduler2.schedule_absolute(datetime.utcnow() + timedelta(seconds=3), action, scheduler2.now)
# print "1", scheduler1.now()
# scheduler1.advance_to(starttime + timedelta(seconds=1))
# print "2", scheduler1.now()
# scheduler1.advance_to(starttime + timedelta(seconds=2))
# print "3", scheduler1.now()
# scheduler1.advance_to(starttime + timedelta(seconds=3))
# print "4", scheduler1.now()
# scheduler1.advance_by(2000)
# print "5", scheduler1.now()


current_ts = datetime_to_unixtimemillis(starttime)
next_ts = Bar.get_next_bar_start_time(current_ts, BarSize.S5)
diff = next_ts - current_ts

Observable.timer(int(diff), 1000, realtime_clock.scheduler).subscribe(on_next=action)

time.sleep(10000)
