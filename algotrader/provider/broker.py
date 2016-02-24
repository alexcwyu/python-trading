import abc

from algotrader.event.order import *
from algotrader.provider import *
from algotrader.tools.singleton import *
from algotrader.trading.event_bus import EventBus


class Broker(Provider, OrderEventHandler):
    __metaclass__ = abc.ABCMeta

    def start(self):
        pass


@singleton
class Simulator(Broker, MarketDataEventHandler):
    ID = "Simulator"

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def stop(self):
        pass

    def on_bar(self, bar):
        print "[%s] %s" % (self.__class__.__name__, bar)

    def on_quote(self, quote):
        print "[%s] %s" % (self.__class__.__name__, quote)

    def on_trade(self, trade):
        print "[%s] %s" % (self.__class__.__name__, trade)

    def on_order(self, order):
        print "[%s] %s" % (self.__class__.__name__, order)


broker_mapping = {
    Simulator.ID: Simulator()
}


def getBroker(broker_id):
    return broker_mapping[broker_id]
