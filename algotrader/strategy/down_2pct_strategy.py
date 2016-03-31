from algotrader.event.order import OrdAction
from algotrader.strategy.strategy import Strategy
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.technical.roc import ROC
from algotrader.utils import logger


class Down2PctStrategy(Strategy):
    def __init__(self, stg_id, broker_id, feed, portfolio, instrument, qty=1000):
        super(Down2PctStrategy, self).__init__(stg_id, broker_id, feed, portfolio)
        self.day_count = 0
        self.order = None
        self.qty = qty
        self.close = inst_data_mgr.get_series("Bar.%s.86400.Close" % instrument)
        self.roc = ROC(self.close, 1)

    def on_bar(self, bar):
        if self.order is None:
            if self.roc.now() < -0.02:
                logger.info("%s,B,%.2f" % (bar.timestamp, bar.close))
                self.order = self.new_market_order(instrument=bar.instrument, action=OrdAction.BUY, qty=self.qty)
                self.day_count = 0
        else:
            self.day_count += 1
            if self.day_count >= 5:
                logger.info("%s,S,%.2f" % (bar.timestamp, bar.close))
                self.new_market_order(instrument=bar.instrument, action=OrdAction.SELL, qty=self.qty)
                self.order = None

