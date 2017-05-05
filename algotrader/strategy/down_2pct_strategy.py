from algotrader.model.trade_data_pb2 import *
from algotrader.technical.roc import ROC
from algotrader.trading.strategy import Strategy


class Down2PctStrategy(Strategy):
    def __init__(self, stg_id: str, state: StrategyState = None):
        super(Down2PctStrategy, self).__init__(stg_id=stg_id, state=state)
        self.day_count = 0
        self.order = None

    def _start(self, app_context):
        self.qty = self._get_stg_config("qty", default=1)

        self.close = self.app_context.inst_data_mgr.get_series(
            "Bar.%s.Time.86400" % app_context.app_config.get_app_config("instrumentIds")[0])
        self.close.start(app_context)

        self.roc = ROC(self.close, 'close', 1)
        self.roc.start(app_context)

        super(Down2PctStrategy, self)._start(app_context)

    def _stop(self):
        super(Down2PctStrategy, self)._stop()

    def on_bar(self, bar):
        if self.order is None:
            if self.roc.now('value') < -0.02:
                # logger.info("%s,B,%.2f" % (bar.timestamp, bar.close))
                self.order = self.market_order(inst_id=bar.inst_id, action=Buy, qty=self.qty)
                self.day_count = 0
        else:
            self.day_count += 1
            if self.day_count >= 5:
                # logger.info("%s,S,%.2f" % (bar.timestamp, bar.close))
                self.market_order(inst_id=bar.inst_id, action=Sell, qty=self.qty)
                self.order = None
