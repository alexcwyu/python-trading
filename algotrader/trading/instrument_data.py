from algotrader.event.event_bus import *
from algotrader.event.market_data import *
from algotrader.tools import *


@singleton
class InstrumentDataManager(MarketDataEventHandler):
    def __init__(self):
        pass

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))


inst_data_mgr = InstrumentDataManager()
