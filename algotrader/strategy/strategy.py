from algotrader.trading.portfolio import Portfolio
from algotrader.trading.order_mgr import order_mgr
from algotrader.event.order import OrdType, TIF, ExecutionEventHandler, Order
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.event.event_bus import EventBus
from algotrader.trading import clock
from algotrader.tools import logger
from algotrader.strategy.strategy_mgr import stg_mgr

from algotrader.provider.broker_mgr import broker_mgr

class Strategy(ExecutionEventHandler, MarketDataEventHandler):
    def __init__(self, stg_id, broker_id, feed, portfolio):
        self.stg_id = stg_id
        self.__broker_id = broker_id
        self.__feed = feed
        self.__portfolio = portfolio
        stg_mgr.add_strategy(self)

    def start(self):
        broker = broker_mgr.get_broker(broker_id=self.__broker_id)
        broker.start()
        self.__portfolio.start()
        EventBus.data_subject.subscribe(self.on_next)
        self.__feed.start()

    def on_bar(self, bar):
        logger.debug("[%s] %s" % (self.__class__.__name__, bar))
        self.__portfolio.on_bar(bar)

    def on_quote(self, quote):
        logger.debug("[%s] %s" % (self.__class__.__name__, quote))
        self.__portfolio.on_quote(quote)

    def on_trade(self, trade):
        logger.debug("[%s] %s" % (self.__class__.__name__, trade))
        self.__portfolio.on_trade(trade)

    def on_ord_upd(self, ord_upd):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_upd))
        self.__portfolio.on_ord_upd(ord_upd)

    def on_exec_report(self, exec_report):
        logger.debug("[%s] %s" % (self.__class__.__name__, exec_report))
        self.__portfolio.on_exec_report(exec_report)

    def new_market_order(self, instrument, action, qty, tif=TIF.DAY):
        self.new_order(instrument, OrdType.MARKET, action, qty, 0.0, tif)

    def new_limit_order(self, instrument, action, qty, price, tif=TIF.DAY):
        self.new_order(instrument, OrdType.LIMIT, action, qty, price, tif)

    def new_order(self, instrument, ord_type, action, qty, price, tif=TIF.DAY):
        order = Order(instrument=instrument, timestamp=clock.default_clock.current_date_time(),
                      ord_id=order_mgr.next_ord_id(), stg_id=self.__stg_id, broker_id=self.__broker_id, action=action, type=ord_type,
                      tif=tif, qty=qty,
                      limit_price=price)
        order = order_mgr.send_order(order)
        self.__portfolio.on_order(order)
