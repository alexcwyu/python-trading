import abc
from algotrader.event.market_data import *
from algotrader.tools.singleton import *
from algotrader.trading.event_bus import *
import datetime

class Clock(object):
    def current_date_time(self):
        return None


@singleton
class RealTimeClock(Clock):
    def current_date_time(self):
        return datetime.datetime.now()

@singleton
class SimulationClock(Clock, MarketDataEventHandler):
    def current_date_time(self):
        return None

    def on_bar(self, bar):
        print "[%s] %s" % (self.__class__.__name__, bar)

    def on_quote(self, quote):
        print "[%s] %s" % (self.__class__.__name__, quote)

    def on_trade(self, trade):
        print "[%s] %s" % (self.__class__.__name__, trade)


clock = RealTimeClock()
print clock.current_date_time()