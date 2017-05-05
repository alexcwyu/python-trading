from algotrader.model.trade_data_pb2 import *
from algotrader.trading.strategy import Strategy


class MertonOptimalBaby(Strategy):
    """
    This is the baby version that assume appreciation rate and the volatility of the underlying is known
    in advance before constructing the strategy
    in reality this is not true
    So for more advanced version the strategy itself should able to call statistical inference logic to
    get the appreciation rate and volatility of the asset

    So now this class is used as testing purpose
    """

    def __init__(self, stg_id: str, state: StrategyState = None):
        super(MertonOptimalBaby, self).__init__(stg_id=stg_id, state=state)
        self.buy_order = None

    def _start(self, app_context):
        self.arate = self._get_stg_config("arate", default=1)
        self.vol = self._get_stg_config("vol", default=1)

        self.bar = self.app_context.inst_data_mgr.get_series(
            "Bar.%s.Time.86400" % app_context.app_config.get_app_config("instrumentIds")[0])

        self.bar.start(app_context)

        self.optimal_weight = self.arate / self.vol ** 2  # assume risk free rate is zero

        super(MertonOptimalBaby, self)._start(app_context)

    def _stop(self):
        super(MertonOptimalBaby, self)._stop()

    def on_bar(self, bar):
        # we have to rebalance on each bar
        # print bar
        portfolio = self.get_portfolio()
        allocation = portfolio.total_equity * self.optimal_weight
        delta = allocation - portfolio.stock_value
        if delta > 0:
            qty = delta / bar.close  # assume no lot size here
            self.market_order(inst_id=bar.inst_id, action=Buy, qty=qty)
        else:
            qty = -delta / bar.close  # assume no lot size here
            self.market_order(inst_id=bar.inst_id, action=Sell, qty=qty)
