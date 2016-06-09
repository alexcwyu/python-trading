from algotrader.event.order import OrdAction
from algotrader.strategy.strategy import Strategy
from algotrader.technical.ma import SMA
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.utils import logger


class SMAStrategy(Strategy):
    def __init__(self, stg_id, portfolio, instrument, qty, trading_config):
        super(SMAStrategy, self).__init__(stg_id, portfolio, instrument, trading_config)
        self.order = None
        self.qty = qty
        self.bar = inst_data_mgr.get_series("Bar.%s.Time.86400" % instrument)
        self.sma_fast = SMA(self.bar, 'close', 10)
        self.sma_slow = SMA(self.bar, 'close', 25)

    def on_bar(self, bar):
        if self.order is None and self.sma_fast.now('value') > self.sma_slow.now('value'):
            logger.info("%s,B,%.2f,%.2f,%.2f" % (
                bar.timestamp, bar.close, self.sma_fast.now('value'), self.sma_slow.now('value')))
            self.order = self.market_order(instrument=bar.instrument, action=OrdAction.BUY, qty=self.qty)
        elif self.order is not None and self.sma_fast.now('value') < self.sma_slow.now('value'):
            logger.info("%s,S,%.2f,%.2f,%.2f" % (
                bar.timestamp, bar.close, self.sma_fast.now('value'), self.sma_slow.now('value')))
            self.market_order(instrument=bar.instrument, action=OrdAction.SELL, qty=self.qty)
            self.order = None
