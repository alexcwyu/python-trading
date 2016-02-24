from algotrader.event.market_data import *
from algotrader.tools.singleton import *
from algotrader.trading.event_bus import *


@singleton
class InstrumentDataManager(MarketDataEventHandler):
    def __init__(self):
        EventBus.data_subject.subscribe(self.on_next)

    def on_bar(self, bar):
        print "[%s] %s" % (self.__class__.__name__, bar)

    def on_quote(self, quote):
        print "[%s] %s" % (self.__class__.__name__, quote)

    def on_trade(self, trade):
        print "[%s] %s" % (self.__class__.__name__, trade)


inst_data_mgr = InstrumentDataManager()
