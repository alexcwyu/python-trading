import abc
import threading

import ccxt
import gevent

from algotrader.model.market_data_pb2 import *
from algotrader.model.trade_data_pb2 import *
from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed


class CCXTBroker(Broker, Feed):
    __metaclass__ = abc.ABCMeta

    def __init__(self, exch_id):
        super(CCXTBroker, self).__init__()
        self._exch = getattr(ccxt, exch_id)()
        self._id = exch_id
        self._trade_subscriptions = set()
        self._bar_subscriptions = set()
        self._quote_subscriptions = set()
        self._orderbook_subscriptions = set()

    def id(self):
        return self._id

    def _start(self, app_context=None):

        self.ref_data_mgr = self.app_context.ref_data_mgr
        self.data_event_bus = self.app_context.event_bus.data_subject
        self.execution_event_bus = self.app_context.event_bus.execution_subject

        self.gevent_sleep = 2
        self.use_gevent = True
        if self.use_gevent:
            gevent.spawn(self.__loop)
        else:
            thread = threading.Thread(target=self.__loop)
            thread.daemon = self.daemon
            thread.start()

    def send_order(self, new_ord_req: NewOrderRequest) -> None:
        raise NotImplementedError

    def cancel_order(self, ord_cancel_req: OrderCancelRequest) -> None:
        raise NotImplementedError

    def replace_order(self, ord_replace_req: OrderReplaceRequest) -> None:
        raise NotImplementedError

    def subscribe_mktdata(self, *sub_reqs):
        for sub_req in sub_reqs:
            symbol = None
            if sub_req.type.from_date:
                req_func = self.__req_hist_data
            elif sub_req.type == MarketDataSubscriptionRequest.MarketDepth:
                self._orderbook_subscriptions.add(symbol)
            elif sub_req.type == MarketDataSubscriptionRequest.Bar:
                self._bar_subscriptions.add(symbol)
            elif sub_req.type == MarketDataSubscriptionRequest.Trade:
                self._trade_subscriptions.add(symbol)
            elif sub_req.type == MarketDataSubscriptionRequest.Quote:
                self._quote_subscriptions.add(symbol)

    def __req_hist_data(self, symbol):
        pass

    def __req_all_trades(self):
        for symbol in self._trade_subscriptions:
            self._exch.fetch_order_book(symbol)

    def __req_all_bars(self):
        for symbol in self._bar_subscriptions:
            self._exch.fetch_order_book(symbol)

    def __req_all_orderbooks(self):
        subs = self._orderbook_subscriptions + self._quote_subscriptions
        for symbol in subs:
            self._exch.fetch_order_book(symbol)

    def __loop(self):
        run = True
        while run:
            self.__req_all_trades()
            self.__req_all_bars()
            self.__req_all_orderbooks()
            gevent.sleep(self.gevent_sleep)

    def unsubscribe_mktdata(self, *sub_reqs):
        for sub_req in sub_reqs:
            symbol = None
            if not sub_req.type.from_date:
                if sub_req.type == MarketDataSubscriptionRequest.MarketDepth:
                    self._orderbook_subscriptions.remove(symbol)
                if sub_req.type == MarketDataSubscriptionRequest.Bar:
                    self._bar_subscriptions.remove(symbol)
                if sub_req.type == MarketDataSubscriptionRequest.Trade:
                    self._trade_subscriptions.remove(symbol)
                if sub_req.type == MarketDataSubscriptionRequest.Quote:
                    self._quote_subscriptions.remove(symbol)
