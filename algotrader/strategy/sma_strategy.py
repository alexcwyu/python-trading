from algotrader.event.order import OrdAction
from algotrader.strategy.strategy import Strategy
from algotrader.technical.ma import SMA
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.utils import logger


class SMAStrategy(Strategy):
    def __init__(self, stg_id, portfolio, instrument, qty, trading_config):
        super(SMAStrategy, self).__init__(stg_id, portfolio, instrument, trading_config)
        self.buy_order = None
        self.qty = qty
        self.bar = inst_data_mgr.get_series("Bar.%s.Time.86400" % instrument)
        self.sma_fast = SMA(self.bar, 'close', length=10)
        self.sma_slow = SMA(self.bar, 'close', length=25)

    def on_bar(self, bar):
        if self.buy_order is None and self.sma_fast.now('value') > self.sma_slow.now('value'):
            self.buy_order = self.market_order(inst_id=bar.inst_id, action=OrdAction.BUY, qty=self.qty)
            logger.info("%s,B,%s,%s,%.2f,%.2f,%.2f" % (
                bar.timestamp, self.buy_order.cl_id, self.buy_order.cl_ord_id, bar.close, self.sma_fast.now('value'), self.sma_slow.now('value')))
        elif self.buy_order is not None and self.sma_fast.now('value') < self.sma_slow.now('value'):
            sell_order = self.market_order(inst_id=bar.inst_id, action=OrdAction.SELL, qty=self.qty)
            logger.info("%s,S,%s,%s,%.2f,%.2f,%.2f" % (
                bar.timestamp, sell_order.cl_id, sell_order.cl_ord_id, bar.close, self.sma_fast.now('value'), self.sma_slow.now('value')))
            self.buy_order = None
