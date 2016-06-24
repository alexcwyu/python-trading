import abc
import time

from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.utils import logger
from algotrader.utils.singleton import singleton


class Clock:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def current_date_time(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_reminder(self, on_reminder, datetime, data=None):
        raise NotImplementedError()


@singleton
class RealTimeClock(Clock):
    def current_date_time(self):
        return int(time.time())

    def add_reminder(self, on_reminder, datetime, data=None):
        return None


@singleton
class SimulationClock(Clock, MarketDataEventHandler):
    def __init__(self):
        self.__current_time = None

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def current_date_time(self):
        return self.__current_time

    def add_reminder(self, on_reminder, datetime, data=None):
        return None

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__current_time = bar.timestamp

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__current_time = quote.timestamp

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__current_time = trade.timestamp

    def add_reminder(self, on_reminder, datetime, data=None):
        return None


realtime_clock = RealTimeClock()

simluation_clock = SimulationClock()

default_clock = realtime_clock  # default setting
