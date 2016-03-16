from algotrader.event.event_bus import *
from algotrader.event.market_data import *
from algotrader.tools import *


#@singleton
class InstrumentDataManager(MarketDataEventHandler):
    def __init__(self):
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__bar_dict[bar.instrument] = bar

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__quote_dict[quote.instrument] = quote

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__trade_dict[trade.instrument] = trade

    def get_bar(self, instrument):
        if instrument in self.__bar_dict:
            return self.__bar_dict[instrument]
        return None

    def get_quote(self, instrument):
        if instrument in self.__quote_dict:
            return self.__quote_dict[instrument]
        return None

    def get_trade(self, instrument):
        if instrument in self.__trade_dict:
            return self.__trade_dict[instrument]
        return None

    def get_latest_price(self, instrument):
        if instrument in self.__trade_dict:
            return self.__trade_dict[instrument].price
        elif instrument in self.__quote_dict:
            return self.__quote_dict[instrument].mid()
        elif instrument in self.__bar_dict:
            return self.__bar_dict[instrument].close_or_adj_close()
        return None

    def clear(self):
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}


inst_data_mgr = InstrumentDataManager()
