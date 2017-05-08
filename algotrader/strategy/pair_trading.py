import math

import rx
from rx.subjects import BehaviorSubject

from algotrader.model.trade_data_pb2 import *
from algotrader.strategy import Strategy
from algotrader import Context


class PairTradingWithOUSpread(Strategy):
    """
    This is the baby version that assume the asset we are trading paris
    that the spread follows Ornstein-Uhlenbeck mean reverting process with known parameters in advance
    in reality this is not true
    So for more advanced version the strategy itself should able to call statistical inference logic to
    get the appreciation rate and volatility of the asset

    So now this class is used as testing purpose
    """

    def __init__(self, stg_id: str, state: StrategyState = None):
        super(PairTradingWithOUSpread, self).__init__(stg_id=stg_id, state=state)
        self.buy_order = None

    def _start(self, app_context: Context) -> None:
        self.ou_params = self._get_stg_config("ou_params", default=1)
        self.gamma = self._get_stg_config("gamma", default=1)

        self.instruments = app_context.config.get_app_config("instrumentIds")
        self.bar_0 = self.app_context.inst_data_mgr.get_series(
            "Bar.%s.Time.86400" % self.instruments[0])
        self.bar_1 = self.app_context.inst_data_mgr.get_series(
            "Bar.%s.Time.86400" % self.instruments[1])

        self.bar_0.start(app_context)
        self.bar_1.start(app_context)

        self.log_spot_0 = BehaviorSubject(0)
        self.log_spot_1 = BehaviorSubject(0)
        self.spread_stream = rx.Observable \
            .zip(self.log_spot_0, self.log_spot_1, lambda x, y: [x, y, x - y]) \
            .subscribe(self.rebalance)

        super(PairTradingWithOUSpread, self)._start(app_context)

    def _stop(self):
        super(PairTradingWithOUSpread, self)._stop()

    def on_bar(self, bar):
        # logger.info("%s,%s,%.2f" % (bar.inst_id, bar.timestamp, bar.close))
        if bar.inst_id == self.instruments[0]:
            self.log_spot_0.on_next(math.log(bar.close))
        elif bar.inst_id == self.instruments[1]:
            self.log_spot_1.on_next(math.log(bar.close))

    def rebalance(self, spread_triple):
        if spread_triple[0] == 0:
            return
        # we have to rebalance on each bar
        k = self.ou_params['k']
        eta = self.ou_params['eta']
        theta = self.ou_params['theta']
        spread = spread_triple[2]

        weight = k * (spread - theta) / eta ** 2
        portfolio = self.get_portfolio()
        allocation_0 = -portfolio.total_equity * weight
        allocation_1 = portfolio.total_equity * weight
        # TODO: need to check if the portoflio.positions is empty
        delta_0 = allocation_0
        delta_1 = allocation_1
        if self.instruments[0] in portfolio.positions.keys():
            delta_0 = allocation_0 - portfolio.positions[self.instruments[0]].current_value()
        if self.instruments[1] in portfolio.positions.keys():
            delta_1 = allocation_1 - portfolio.positions[self.instruments[1]].current_value()

        qty = abs(delta_0) / spread_triple[0]  # assume no lot size here
        if delta_0 > 0:
            self.market_order(inst_id=self.instruments[0], action=Buy, qty=qty)
        else:
            self.market_order(inst_id=self.instruments[0], action=Sell, qty=qty)

        qty = abs(delta_1) / spread_triple[1]  # assume no lot size here
        if delta_1 > 0:
            self.market_order(inst_id=self.instruments[1], action=Buy, qty=qty)
        else:
            self.market_order(inst_id=self.instruments[1], action=Sell, qty=qty)
