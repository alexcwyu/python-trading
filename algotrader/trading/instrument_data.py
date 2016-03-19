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

        self.__bar_series = defaultdict(TimeSeries)
        self.__quote_series = defaultdict(TimeSeries)
        self.__trade_series = defaultdict(TimeSeries)

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__bar_dict[bar.instrument] = bar

        self.__bar_series[bar.instrument].add(bar.timestamp, bar.close_or_adj_close())

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__quote_dict[quote.instrument] = quote
        self.__quote_series[quote.instrument].add(quote.timestamp, quote.mid())

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__trade_dict[trade.instrument] = trade
        self.__trade_series[trade.instrument].add(trade.timestamp, trade.price)

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

    def get_bar_series(self):
        return self.__bar_series

    def get_quote_series(self):
        return self.__quote_series

    def get_trade_series(self):
        return self.__trade_series

    def clear(self):
        self.__bar_dict = {}
        self.__quote_dict = {}
        self.__trade_dict = {}
        self.__bar_series = defaultdict(TimeSeries)
        self.__quote_series = defaultdict(TimeSeries)
        self.__trade_series = defaultdict(TimeSeries)


inst_data_mgr = InstrumentDataManager()
