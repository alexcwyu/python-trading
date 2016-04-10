from algotrader.event.order import OrdAction
from algotrader.strategy.strategy import Strategy
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.technical.ma import SMA
from algotrader.utils import logger


class SMAStrategy(Strategy):
    def __init__(self, stg_id, broker_id, feed, portfolio, instrument, qty=1000):
        super(SMAStrategy, self).__init__(stg_id, broker_id, feed, portfolio)
        self.order = None
        self.qty = qty
        self.close = inst_data_mgr.get_series("Bar.%s.86400.Close" % instrument)
        self.sma_fast = SMA(self.close, 10)
        self.sma_slow = SMA(self.close, 25)

    def on_bar(self, bar):
        if self.order is None and self.sma_fast.now() > self.sma_slow.now():
            logger.info("%s,B,%.2f,%.2f,%.2f" % (
                bar.timestamp, bar.close, self.sma_fast.now(), self.sma_slow.now()))
            self.order = self.market_order(instrument=bar.instrument, action=OrdAction.BUY, qty=self.qty)
        elif self.order is not None and self.sma_fast.now() < self.sma_slow.now():
            logger.info("%s,S,%.2f,%.2f,%.2f" % (
                bar.timestamp, bar.close, self.sma_fast.now(), self.sma_slow.now()))
            self.market_order(instrument=bar.instrument, action=OrdAction.SELL, qty=self.qty)
            self.order = None
