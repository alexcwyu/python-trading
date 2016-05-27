from datetime import date

from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import MarketDataEventHandler, Bar, BarSize, BarType
from algotrader.event.order import OrdType, TIF, ExecutionEventHandler, Order
from algotrader.provider import broker_mgr, feed_mgr, HistDataSubscriptionKey, SubscriptionKey
from algotrader.provider.broker.ib.ib_broker import IBBroker
from algotrader.provider.broker.simulator import Simulator
from algotrader.provider.feed.csv import CSVDataFeed
from algotrader.strategy.strategy_mgr import stg_mgr
from algotrader.trading.order_mgr import order_mgr
from algotrader.trading.ref_data import inmemory_ref_data_mgr
from algotrader.utils import logger, clock


class TradingConfig(object):
    def __init__(self, broker_id, feed_id,
                 data_type,
                 bar_type,
                 bar_size):
        self.broker_id = broker_id
        self.feed_id = feed_id
        self.data_type = data_type
        self.bar_type = bar_type
        self.bar_size = bar_size


class LiveTradingConfig(TradingConfig):
    def __init__(self, broker_id=IBBroker.ID, feed_id=IBBroker.ID, data_type=Bar, bar_type=BarType.Time,
                 bar_size=BarSize.S1):
        super(LiveTradingConfig, self).__init__(broker_id=broker_id, feed_id=feed_id, data_type=data_type,
                                                bar_type=bar_type, bar_size=bar_size)


class BacktestingConfig(TradingConfig):
    def __init__(self, broker_id=Simulator.ID, feed_id=CSVDataFeed.ID, data_type=Bar, bar_type=BarType.Time,
                 bar_size=BarSize.D1, from_date=date(2010, 1, 1), to_date=date.today()):
        super(BacktestingConfig, self).__init__(broker_id=broker_id, feed_id=feed_id, data_type=data_type,
                                                bar_type=bar_type, bar_size=bar_size)
        self.from_date = from_date
        self.to_date = to_date


class Strategy(ExecutionEventHandler, MarketDataEventHandler):
    def __init__(self, stg_id, portfolio, instrument,
                 trading_config, ref_data_mgr = None):
        self.stg_id = stg_id
        self.__portfolio = portfolio
        self.__instrument = instrument
        self.__trading_config = trading_config
        self.__next_ord_id = 0
        self.__ref_data_mgr = ref_data_mgr if ref_data_mgr else inmemory_ref_data_mgr

        stg_mgr.add_strategy(self)

    def __get_next_ord_id(self):
        next_ord_id = self.__next_ord_id
        self.__next_ord_id += 1
        return next_ord_id

    def start(self):
        self.__portfolio.start()
        EventBus.data_subject.subscribe(self.on_next)

        broker = broker_mgr.get(self.__trading_config.broker_id)
        broker.start()

        feed = feed_mgr.get(self.__trading_config.feed_id)
        feed.start()


        inst = self.__ref_data_mgr.get_inst(symbol=self.__instrument)
        if isinstance(self.__trading_config, BacktestingConfig):

            sub_key = HistDataSubscriptionKey(inst_id=inst.inst_id,
                                              provider_id=self.__trading_config.feed_id,
                                              data_type=self.__trading_config.data_type,
                                              bar_type=self.__trading_config.bar_type,
                                              bar_size=self.__trading_config.bar_size,
                                              from_date=self.__trading_config.from_date,
                                              to_date=self.__trading_config.to_date)

        else:
            sub_key = SubscriptionKey(inst_id=inst.inst_id,
                                      provider_id=self.__trading_config.feed_id,
                                      data_type=self.__trading_config.data_type,
                                      bar_type=self.__trading_config.bar_type,
                                      bar_size=self.__trading_config.bar_size)
        feed.subscribe_mktdata(sub_key)

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
                      ord_id=order_mgr.next_ord_id(), stg_id=self.stg_id, broker_id=self.__trading_config.broker_id, action=action,
                      type=ord_type,
                      tif=tif, qty=qty,
                      limit_price=price,
                      cl_ord_id=self.__get_next_ord_id())
        self.__portfolio.on_order(order)
        order = order_mgr.send_order(order)
        return order

    def get_portfolio(self):
        return self.__portfolio
