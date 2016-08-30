from algotrader.event.event_bus import EventBus
from algotrader.event.event_handler import MarketDataEventHandler, ExecutionEventHandler
from algotrader.event.order import OrdAction, OrdType, TIF, NewOrderRequest, OrderReplaceRequest, \
    OrderCancelRequest
from algotrader.provider.persistence.persist import Persistable
from algotrader.provider.provider import broker_mgr, feed_mgr
from algotrader.provider.subscription import SubscriptionKey, HistDataSubscriptionKey
from algotrader.strategy.strategy_mgr import stg_mgr
from algotrader.trading.config import BacktestingConfig
from algotrader.trading.position import PositionHolder
from algotrader.trading.ref_data import inmemory_ref_data_mgr, get_ref_data_mgr
from algotrader.trading.portfolio_mgr import portf_mgr
from algotrader.utils.clock import get_clock


class Strategy(PositionHolder, ExecutionEventHandler, MarketDataEventHandler, Persistable):
    __slots__ = (
        'stg_id',
        'trading_config',
        'next_ord_id',
        'ord_req',
        'order',
    )

    def __init__(self, stg_id=None, next_ord_id=0, trading_config=None, ref_data_mgr=None):
        super(Strategy, self).__init__()
        self.stg_id = stg_id
        self.trading_config = trading_config
        self.next_ord_id = next_ord_id
        self.ord_req = {}
        self.order = {}

        self.__ref_data_mgr = ref_data_mgr if ref_data_mgr else get_ref_data_mgr(self.trading_config.ref_data_mgr_type) if self.trading_config else None
        self.__started = False
        stg_mgr.add_strategy(self)

    def __get_next_ord_id(self):
        next_ord_id = self.next_ord_id
        self.next_ord_id += 1
        return next_ord_id

    def start(self):
        if not self.__started:

            self.__ref_data_mgr = self.__ref_data_mgr if self.__ref_data_mgr else get_ref_data_mgr(self.trading_config.ref_data_mgr_type)
            self.__portfolio = portf_mgr.get_portfolio(self.trading_config.portfolio_id)
            self.__feed = feed_mgr.get(self.trading_config.feed_id) if self.trading_config else None
            self.__instruments = self.__ref_data_mgr.get_insts(self.trading_config.instrument_ids)
            self.__started = True
            self.__portfolio.start()
            self.__clock = get_clock(self.trading_config.clock_type)

            self.__broker = broker_mgr.get(self.trading_config.broker_id)
            self.__broker.start()

            self.__event_subscription = EventBus.data_subject.subscribe(self.on_next)
            self._subscribe_market_data(self.__instruments)
            self.__feed.start()

    def stop(self):
        if self.__started:
            self.__event_subscription.dispose()


    def _subscribe_market_data(self, instruments):
        for instrument in instruments:
            for subscription_type in self.trading_config.subscription_types:
                if isinstance(self.trading_config, BacktestingConfig):

                    sub_key = HistDataSubscriptionKey(inst_id=instrument.inst_id,
                                                      provider_id=self.trading_config.feed_id,
                                                      subscription_type=subscription_type,
                                                      from_date=self.trading_config.from_date,
                                                      to_date=self.trading_config.to_date)

                else:
                    sub_key = SubscriptionKey(inst_id=instrument.inst_id,
                                              provider_id=self.trading_config.feed_id,
                                              subscription_type=subscription_type)
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
            ord_req = self.ord_req[exec_report.cl_ord_id]
            direction = 1 if ord_req.action == OrdAction.BUY else -1
            if exec_report.last_qty > 0:
                self.add_position(exec_report.inst_id, exec_report.cl_id, exec_report.cl_ord_id,
                                  direction * exec_report.last_qty)
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
        req = NewOrderRequest(timestamp=self.__clock.now(),
                              cl_id=self.stg_id,
                              cl_ord_id=self.__get_next_ord_id(),
                              portf_id=self.__portfolio.portf_id,
                              broker_id=self.trading_config.broker_id,
                              inst_id=inst_id,
                              action=action,
                              type=type,
                              qty=qty,
                              limit_price=limit_price,
                              stop_price=stop_price,
                              tif=tif,
                              oca_tag=oca_tag,
                              params=params)
        self.ord_req[req.cl_ord_id] = req
        order = self.__portfolio.send_order(req)
        self.order[order.cl_ord_id] = order
        self.get_position(order.inst_id).add_order(order)
        return order

    def cancel_order(self, cl_ord_id=None):
        req = OrderCancelRequest(timestamp=self.__clock.now(),
                                 cl_id=self.stg_id, cl_ord_id=cl_ord_id)
        order = self.__portfolio.cancel_order(req)
        return order

    def replace_order(self, cl_ord_id=None, type=None, qty=None, limit_price=None, stop_price=None, tif=None):
        req = OrderReplaceRequest(timestamp=self.__clock.now(),
                                  cl_id=self.stg_id, cl_ord_id=cl_ord_id, type=type, qty=qty, limit_price=limit_price,
                                  stop_price=stop_price, tif=tif)
        order = self.__portfolio.replace_order(req)
        return order

    def get_portfolio(self):
        return self.__portfolio
