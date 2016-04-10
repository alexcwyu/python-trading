from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.event.order import OrdType, TIF, ExecutionEventHandler, Order
from algotrader.provider import broker_mgr
from algotrader.strategy.strategy_mgr import stg_mgr
from algotrader.trading.order_mgr import order_mgr
from algotrader.utils import logger, clock
from algotrader.trading.instrument_data import inst_data_mgr


class Strategy(ExecutionEventHandler, MarketDataEventHandler):
    def __init__(self, stg_id, broker_id, feed, portfolio):
        self.stg_id = stg_id
        self.__broker_id = broker_id
        self.__feed = feed
        self.__portfolio = portfolio
        self.__next_ord_id = 0
        stg_mgr.add_strategy(self)

    def __get_next_ord_id(self):
        next_ord_id = self.__next_ord_id
        self.__next_ord_id += 1
        return next_ord_id


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

    def market_order(self, instrument, action, qty, tif=TIF.DAY):
        return self.new_order(instrument, OrdType.MARKET, action, qty, 0.0, tif)

    def limit_order(self, instrument, action, qty, price, tif=TIF.DAY):
        return self.new_order(instrument, OrdType.LIMIT, action, qty, price, tif)

    def stop_order(self):
        pass

    def stop_limit_order(self):
        pass

    def close_position(self):
        pass
           


    def new_order(self, instrument, ord_type, action, qty, price, tif=TIF.DAY):
        order = Order(instrument=instrument, timestamp=clock.default_clock.current_date_time(),
                      ord_id=order_mgr.next_ord_id(), stg_id=self.stg_id, broker_id=self.__broker_id, action=action,
                      type=ord_type,
                      tif=tif, qty=qty,
                      limit_price=price,
                      cl_ord_id=self.__get_next_ord_id())
        self.__portfolio.on_order(order)
        order = order_mgr.send_order(order)
        return order

    def get_portfolio(self):
        return self.__portfolio
