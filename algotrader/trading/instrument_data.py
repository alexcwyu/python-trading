from collections import defaultdict

from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.utils import logger
from algotrader.utils.time_series import TimeSeries


class InstrumentDataManager(MarketDataEventHandler):
    def __init__(self):
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}

        self.__series_dict = {}

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__bar_dict[bar.instrument] = bar

        self.get_series("%s.%s" % (bar.id(), "Open")).add(bar.timestamp, bar.open)
        self.get_series("%s.%s" % (bar.id(), "High")).add(bar.timestamp, bar.high)
        self.get_series("%s.%s" % (bar.id(), "Low")).add(bar.timestamp, bar.low)
        self.get_series("%s.%s" % (bar.id(), "Close")).add(bar.timestamp, bar.close)
        self.get_series("%s.%s" % (bar.id(), "AdjClose")).add(bar.timestamp, bar.adj_close)
        self.get_series("%s.%s" % (bar.id(), "Vol")).add(bar.timestamp, bar.vol)
        self.get_series("%s.%s" % (bar.id(), "CloseOrAdjClose")).add(bar.timestamp, bar.close_or_adj_close())

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__quote_dict[quote.instrument] = quote

        self.get_series("%s.%s" % (quote.id(), "Bid")).add(quote.timestamp, quote.bid)
        self.get_series("%s.%s" % (quote.id(), "BidSize")).add(quote.timestamp, quote.bid_size)
        self.get_series("%s.%s" % (quote.id(), "Ask")).add(quote.timestamp, quote.ask())
        self.get_series("%s.%s" % (quote.id(), "AskSize")).add(quote.timestamp, quote.ask_size)
        self.get_series("%s.%s" % (quote.id(), "Mid")).add(quote.timestamp, quote.mid())

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__trade_dict[trade.instrument] = trade

        self.get_series("%s.%s" % (trade.id(), "Price")).add(trade.timestamp, trade.price)
        self.get_series("%s.%s" % (trade.id(), "Size")).add(trade.timestamp, trade.size)

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

    def get_series(self, key):
        if key not in self.__series_dict:
            self.__series_dict[key] = TimeSeries(id=key)
        return self.__series_dict[key]

    def add_series(self, series):
        if series.id not in self.__series_dict:
            self.__series_dict[series.id] = series
            return True
        return False

    def clear(self):
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}
        self.__series_dict = defaultdict(TimeSeries)


inst_data_mgr = InstrumentDataManager()
