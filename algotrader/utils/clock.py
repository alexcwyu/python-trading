import abc
import datetime
import time

from rx.concurrency.mainloopscheduler import GEventScheduler
from rx.concurrency.historicalscheduler import HistoricalScheduler
from rx.concurrency.newthreadscheduler import NewThreadScheduler
from rx.concurrency.eventloopscheduler import EventLoopScheduler


from algotrader.event.event_bus import EventBus
from algotrader.event.event_handler import MarketDataEventHandler
from algotrader.utils import logger
from gevent import monkey
monkey.patch_all()

class Clock:
    __metaclass__ = abc.ABCMeta
    epoch = datetime.datetime.fromtimestamp(0)

    def __init__(self, scheduler):
        self.scheduler = scheduler

    @abc.abstractmethod
    def now(self):
        raise NotImplementedError()

    def schedule_relative(self, time_delta, action, state=None):
        self.scheduler.schedule_relative(time_delta, action, state)

    def schedule_absolute(self, datetime, action, state=None):
        if isinstance(datetime, (long, int)):
            datetime = Clock.unixtimemillis_to_datetime(datetime)
        self.scheduler.schedule_absolute(datetime, action, state)

    @staticmethod
    def datetime_to_unixtimemillis(dt):
        return int((dt - Clock.epoch).total_seconds() * 1000)

    @staticmethod
    def unixtimemillis_to_datetime(timestamp):
        return datetime.datetime.fromtimestamp(timestamp / 1000.0)


class RealTimeScheduler(NewThreadScheduler):
    def __init__(self, thread_factory=None):
        super(RealTimeScheduler, self).__init__()

    def now(self):
        return datetime.datetime.now()

    def schedule_absolute(self, duetime, action, state=None):
        """Schedules an action to be executed at duetime."""
        scheduler = EventLoopScheduler(thread_factory=self.thread_factory, exit_if_empty=True)
        return scheduler.schedule_absolute(duetime, action, state)

    def schedule_relative(self, duetime, action, state=None):
        """Schedules an action to be executed after duetime."""

        scheduler = EventLoopScheduler(thread_factory=self.thread_factory, exit_if_empty=True)
        return scheduler.schedule_relative(duetime, action, state)

class RealTimeClock(Clock):
    def __init__(self, scheduler=None):
        super(RealTimeClock, self).__init__(scheduler=scheduler if scheduler else GEventScheduler())

    def now(self):
        return int(time.time() * 1000)


class SimulationScheduler(HistoricalScheduler):
    def __init__(self, initial_clock=None):
        super(SimulationScheduler, self).__init__(initial_clock)

    @staticmethod
    def add(absolute, relative):
        if isinstance(relative, (long, int)):
            return absolute + datetime.timedelta(milliseconds=relative)
        elif isinstance(relative, float):
            return absolute + datetime.timedelta(seconds=relative)
        return absolute + relative

    def reset(self):
        self.clock = datetime.datetime.fromtimestamp(0)


class SimulationClock(Clock, MarketDataEventHandler):
    def __init__(self, current_timestamp_mills=None, scheduler=None):
        self.__current_timestamp_mills = current_timestamp_mills if current_timestamp_mills else 0
        super(SimulationClock, self).__init__(scheduler=scheduler if scheduler else SimulationScheduler(
            initial_clock=self.__current_timestamp_mills / 1000))

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def now(self):
        return self.__current_timestamp_mills

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.update_time(bar.timestamp)

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.update_time(quote.timestamp)

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.update_time(trade.timestamp)

    def update_time(self, timestamp):
        self.__current_timestamp_mills = timestamp
        self.scheduler.advance_to(Clock.unixtimemillis_to_datetime(timestamp))

    def reset(self):
        self.__current_timestamp_mills = 0
        if self.scheduler:
            self.scheduler.stop()
        self.scheduler = SimulationScheduler(initial_clock=self.__current_timestamp_mills / 1000)


realtime_clock = RealTimeClock()

simluation_clock = SimulationClock()

default_clock = realtime_clock  # default setting
