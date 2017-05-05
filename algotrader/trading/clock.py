from gevent import monkey

monkey.patch_time()
monkey.patch_socket()

import abc
import datetime
import time

from rx.concurrency.eventloopscheduler import EventLoopScheduler
from rx.concurrency.historicalscheduler import HistoricalScheduler
from rx.concurrency.mainloopscheduler import GEventScheduler
from rx.concurrency.newthreadscheduler import NewThreadScheduler

from algotrader.trading.event import MarketDataEventHandler
from algotrader.utils.logging import logger
from algotrader.utils.date import unixtimemillis_to_datetime
from algotrader import Startable, HasId


class Clock(Startable, HasId):
    __metaclass__ = abc.ABCMeta

    Simulation = "Simulation"
    RealTime = "RealTime"

    epoch = datetime.datetime.fromtimestamp(0)

    def __init__(self, scheduler):
        super(Clock, self).__init__()
        self.scheduler = scheduler

    @abc.abstractmethod
    def now(self):
        raise NotImplementedError()

    def schedule_relative(self, time_delta, action, state=None):
        self.scheduler.schedule_relative(time_delta, action, state)

    def schedule_absolute(self, datetime, action, state=None):
        if isinstance(datetime, (int)):
            datetime = unixtimemillis_to_datetime(datetime)
        self.scheduler.schedule_absolute(datetime, action, state)


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

    def id(self):
        return Clock.RealTime

    def _start(self, app_context):
        pass

    def _stop(self):
        pass


class SimulationScheduler(HistoricalScheduler):
    def __init__(self, initial_clock=None):
        super(SimulationScheduler, self).__init__(initial_clock)

    @staticmethod
    def add(absolute, relative):
        if isinstance(relative, (int)):
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

    def _start(self, app_context):
        self.subscription = app_context.event_bus.data_subject.subscribe(self.on_market_data_event)

    def _stop(self):
        if self.subscription:
            self.subscription.dispose()

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
        self.scheduler.advance_to(unixtimemillis_to_datetime(timestamp))

    def reset(self):
        self.__current_timestamp_mills = 0
        if self.scheduler:
            self.scheduler.stop()
        self.scheduler = SimulationScheduler(initial_clock=self.__current_timestamp_mills / 1000)

    def id(self):
        return Clock.Simulation
