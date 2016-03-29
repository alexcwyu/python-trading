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
        close = inst_data_mgr.get_series("Bar.%s.86400.Close" % instrument)
        self.sma_fast = SMA(close, 10)
        self.sma_slow = SMA(close, 25)

    def on_bar(self, bar):
        if self.order is None and self.sma_fast.current_value() > self.sma_slow.current_value():
            logger.info("%s,B,%.2f,%.2f,%.2f" % (
            bar.timestamp, bar.close_or_adj_close(), self.sma_fast.current_value(), self.sma_slow.current_value()))
            self.order = self.new_market_order(instrument=bar.instrument, action=OrdAction.BUY, qty=self.qty)
        elif self.order is not None and self.sma_fast.current_value() < self.sma_slow.current_value():
            logger.info("%s,S,%.2f,%.2f,%.2f" % (
            bar.timestamp, bar.close_or_adj_close(), self.sma_fast.current_value(), self.sma_slow.current_value()))
            self.new_market_order(instrument=bar.instrument, action=OrdAction.SELL, qty=self.qty)
            self.order = None
