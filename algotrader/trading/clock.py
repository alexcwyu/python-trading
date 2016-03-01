import datetime

from algotrader.event import *
from algotrader.tools import *


class Clock:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def current_date_time(self):
        return None


@singleton
class RealTimeClock(Clock):
    def current_date_time(self):
        return datetime.datetime.now()


@singleton
class SimulationClock(Clock, MarketDataEventHandler):
    def __init__(self):
        self.__current_time = None

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def current_date_time(self):
        return self.__current_time

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__current_time = bar.timestamp

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__current_time = quote.timestamp

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__current_time = trade.timestamp


realtime_clock = RealTimeClock()

simluation_clock = SimulationClock()

clock = realtime_clock  # default setting
