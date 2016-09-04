from algotrader.event.order import OrdAction
from algotrader.strategy.strategy import Strategy
from algotrader.trading.instrument_data import inst_data_mgr


class MertonOptimalBaby(Strategy):
    """
    This is the baby version that assume appreciation rate and the volatility of the underlying is known
    in advance before constructing the strategy
    in reality this is not true
    So for more advanced version the strategy itself should able to call statistical inference logic to
    get the appreciation rate and volatility of the asset

    So now this class is used as testing purpose
    """

    def __init__(self, stg_id, arate, vol, trading_config):
        super(MertonOptimalBaby, self).__init__(stg_id=stg_id, trading_config=trading_config)
        self.buy_order = None
        self.arate = arate
        self.vol = vol
        self.bar = inst_data_mgr.get_series("Bar.%s.Time.86400" % trading_config.instrument_ids[0])
        self.optimal_weight = arate / self.vol ** 2  # assume risk free rate is zero

    def on_bar(self, bar):
        # we have to rebalance on each bar
        # print bar
        portfolio = self.get_portfolio()
        allocation = portfolio.total_equity * self.optimal_weight
        delta = allocation - portfolio.stock_value
        if delta > 0:
            qty = delta / bar.close  # assume no lot size here
            self.market_order(inst_id=bar.inst_id, action=OrdAction.BUY, qty=qty)
        else:
            qty = -delta / bar.close  # assume no lot size here
            self.market_order(inst_id=bar.inst_id, action=OrdAction.SELL, qty=qty)
