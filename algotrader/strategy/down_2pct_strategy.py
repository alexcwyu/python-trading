from algotrader.event.order import OrdAction
from algotrader.strategy.strategy import Strategy
from algotrader.technical.roc import ROC
from algotrader.utils import logger


class Down2PctStrategy(Strategy):
    def __init__(self, stg_id=None, trading_config=None):
        super(Down2PctStrategy, self).__init__(stg_id=stg_id, trading_config=trading_config)
        self.day_count = 0
        self.order = None

    def _start(self, app_context, **kwargs):
        self.qty = self.get_config_value("qty", 1)
        self.close = app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % self.trading_config.instrument_ids[0])
        self.roc = ROC(self.close, 'close', 1)
        super(Down2PctStrategy, self)._start(app_context, **kwargs)

    def on_bar(self, bar):
        if self.order is None:
            if self.roc.now('value') < -0.02:
                logger.info("%s,B,%.2f" % (bar.timestamp, bar.close))
                self.order = self.market_order(inst_id=bar.inst_id, action=OrdAction.BUY, qty=self.qty)
                self.day_count = 0
        else:
            self.day_count += 1
            if self.day_count >= 5:
                logger.info("%s,S,%.2f" % (bar.timestamp, bar.close))
                self.market_order(inst_id=bar.inst_id, action=OrdAction.SELL, qty=self.qty)
                self.order = None
