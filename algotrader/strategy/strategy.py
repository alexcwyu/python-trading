from datetime import date

from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import Bar, BarSize, BarType
from algotrader.event.event_handler import MarketDataEventHandler, ExecutionEventHandler
from algotrader.event.order import OrdAction, OrdType, TIF, NewOrderRequest, OrderReplaceRequest, \
    OrderCancelRequest
from algotrader.provider.broker.ib.ib_broker import IBBroker
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.feed.csv_feed import CSVDataFeed
from algotrader.provider.provider import HistDataSubscriptionKey, broker_mgr, feed_mgr
from algotrader.provider.subscription import SubscriptionKey, HistDataSubscriptionKey
from algotrader.strategy.strategy_mgr import stg_mgr
from algotrader.trading.ref_data import inmemory_ref_data_mgr, Instrument
from algotrader.utils import logger
from algotrader.trading.position import Position, PositionHolder
from algotrader.utils.clock import simluation_clock, realtime_clock
from algotrader.trading.trade_data import TradeData


class TradingConfig(object):
    def __init__(self, broker_id, feed_id,
                 data_type,
                 bar_type,
                 bar_size, clock):
        self.broker_id = broker_id
        self.feed_id = feed_id
        self.data_type = data_type
        self.bar_type = bar_type
        self.bar_size = bar_size
        self.clock = clock


class LiveTradingConfig(TradingConfig):
    def __init__(self, broker_id=IBBroker.ID, feed_id=IBBroker.ID, data_type=Bar, bar_type=BarType.Time,
                 bar_size=BarSize.S1):
        super(LiveTradingConfig, self).__init__(broker_id=broker_id, feed_id=feed_id, data_type=data_type,
                                                bar_type=bar_type, bar_size=bar_size, clock=realtime_clock)


class BacktestingConfig(TradingConfig):
    def __init__(self, broker_id=Simulator.ID, feed_id=CSVDataFeed.ID, data_type=Bar, bar_type=BarType.Time,
                 bar_size=BarSize.D1, from_date=date(2010, 1, 1), to_date=date.today()):
        super(BacktestingConfig, self).__init__(broker_id=broker_id, feed_id=feed_id, data_type=data_type,
                                                bar_type=bar_type, bar_size=bar_size, clock=simluation_clock)
        self.from_date = from_date
        self.to_date = to_date


class Strategy(PositionHolder, ExecutionEventHandler, MarketDataEventHandler, TradeData):
    def __init__(self, stg_id, portfolio, instruments,
                 trading_config, ref_data_mgr=None, next_ord_id=0):
        super(Strategy, self).__init__()
        self.stg_id = stg_id
        self.__portfolio = portfolio
        self.__trading_config = trading_config
        self.__next_ord_id = next_ord_id
        self.__ref_data_mgr = ref_data_mgr if ref_data_mgr else inmemory_ref_data_mgr
        self.__instruments = self.__ref_data_mgr.get_insts(instruments)

        self.__feed = feed_mgr.get(self.__trading_config.feed_id)
        stg_mgr.add_strategy(self)
        self.started = False
        self.__ord_req = {}
        self.__order = {}

    def __get_next_ord_id(self):
        next_ord_id = self.__next_ord_id
        self.__next_ord_id += 1
        return next_ord_id

    def start(self):
        if not self.started:
            self.started = True
            self.__portfolio.start()

            broker = broker_mgr.get(self.__trading_config.broker_id)
            broker.start()

            EventBus.data_subject.subscribe(self.on_next)
            self._subscribe_market_data(self.__instruments)
            self.__feed.start()

    def _subscribe_market_data(self, instruments):
        for instrument in instruments:
            self._subscribe_inst(instrument)

    def _subscribe_inst(self, instrument):
        if isinstance(self.__trading_config, BacktestingConfig):

            sub_key = HistDataSubscriptionKey(inst_id=instrument.inst_id,
                                              provider_id=self.__trading_config.feed_id,
                                              data_type=self.__trading_config.data_type,
                                              bar_type=self.__trading_config.bar_type,
                                              bar_size=self.__trading_config.bar_size,
                                              from_date=self.__trading_config.from_date,
                                              to_date=self.__trading_config.to_date)

        else:
            sub_key = SubscriptionKey(inst_id=instrument.inst_id,
                                      provider_id=self.__trading_config.feed_id,
                                      data_type=self.__trading_config.data_type,
                                      bar_type=self.__trading_config.bar_type,
                                      bar_size=self.__trading_config.bar_size)
        self.__feed.subscribe_mktdata(sub_key)

    def id(self):
        return self.stg_id

    def on_bar(self, bar):
        super(Strategy, self).on_bar(bar)

    def on_quote(self, quote):
        super(Strategy, self).on_quote(quote)

    def on_trade(self, trade):
        super(Strategy, self).on_trade(trade)

    def on_market_depth(self, market_depth):
        super(Strategy, self).on_market_depth(market_depth)

    def on_ord_upd(self, ord_upd):
        if ord_upd.cl_id == self.stg_id:
            super(Strategy, self).on_ord_upd(ord_upd)

    def on_exec_report(self, exec_report):
        if exec_report.cl_id == self.stg_id:
            super(Strategy, self).on_exec_report(exec_report)
            ord_req = self.__ord_req[exec_report.cl_ord_id]
            direction = 1 if ord_req.action == OrdAction.BUY else -1
            if exec_report.last_qty > 0:
                self.add_positon(exec_report.inst_id, exec_report.cl_id, exec_report.cl_ord_id, direction * exec_report.last_qty)
                self.update_position_price(exec_report.timestamp, exec_report.inst_id, exec_report.last_price)

    def market_order(self, inst_id, action, qty, tif=TIF.DAY, oca_tag=None, params=None):
        return self.new_order(inst_id=inst_id, action=action, type=OrdType.MARKET, qty=qty, limit_price=0.0, tif=tif,
                              oca_tag=oca_tag, params=params)

    def limit_order(self, inst_id, action, qty, price, tif=TIF.DAY, oca_tag=None, params=None):
        return self.new_order(inst_id=inst_id, action=action, type=OrdType.LIMIT, qty=qty, limit_price=price, tif=tif,
                              oca_tag=oca_tag, params=params)

    def stop_order(self):
        # TODO
        pass

    def stop_limit_order(self):
        # TODO
        pass

    def close_position(self, inst_id):
        # TODO
        pass

    def close_all_positions(self):
        # TODO
        pass

    def new_order(self,
                  inst_id=None, action=None, type=None,
                  qty=0, limit_price=0,
                  stop_price=0, tif=TIF.DAY, oca_tag=None, params=None):
        req = NewOrderRequest(timestamp=self.__trading_config.clock.now(),
                              cl_id=self.stg_id,
                              cl_ord_id=self.__get_next_ord_id(),
                              portf_id=self.__portfolio.portf_id,
                              broker_id=self.__trading_config.broker_id,
                              inst_id=inst_id,
                              action=action,
                              type=type,
                              qty=qty,
                              limit_price=limit_price,
                              stop_price=stop_price,
                              tif=tif,
                              oca_tag=oca_tag,
                              params=params)
        self.__ord_req[req.cl_ord_id] = req
        order = self.__portfolio.send_order(req)
        self.__order[order.cl_ord_id] = order
        self.get_position(order.inst_id).add_order(order)
        return order

    def cancel_order(self, cl_ord_id=None):
        req = OrderCancelRequest(timestamp=self.__trading_config.clock.now(),
                                 cl_id=self.stg_id, cl_ord_id=cl_ord_id)
        order = self.__portfolio.cancel_order(req)
        return order

    def replace_order(self, cl_ord_id=None, type=None, qty=None, limit_price=None, stop_price=None, tif=None):
        req = OrderReplaceRequest(timestamp=self.__trading_config.clock.now(),
                                  cl_id=self.stg_id, cl_ord_id=cl_ord_id, type=type, qty=qty, limit_price=limit_price,
                                  stop_price=stop_price, tif=tif)
        order = self.__portfolio.replace_order(req)
        return order

    def get_portfolio(self):
        return self.__portfolio
