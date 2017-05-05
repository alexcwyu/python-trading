from algotrader.model.trade_data_pb2 import *
from algotrader.technical.talib_wrapper import EMA
from algotrader.trading.strategy import Strategy
from algotrader.utils import logger


class EMAStrategy(Strategy):
    def __init__(self, stg_id: str, state: StrategyState = None):
        super(EMAStrategy, self).__init__(stg_id=stg_id, state=state)
        self.buy_order = None

    def _start(self, app_context):

        self.instruments = app_context.app_config.get_app_config("instrumentIds")
        self.qty = self._get_stg_config("qty", default=1)

        self.bar = self.app_context.inst_data_mgr.get_series(
            "Bar.%s.Time.86400" % self.instruments[0])
        self.bar.start(app_context)

        self.ema_fast = EMA(self.bar, 'close', 10)
        self.ema_fast.start(app_context)

        self.ema_slow = EMA(self.bar, 'close', 25)
        self.ema_slow.start(app_context)

        super(EMAStrategy, self)._start(app_context)

    def _stop(self):
        super(EMAStrategy, self)._stop()

    def on_bar(self, bar):
        if self.buy_order is None and self.ema_fast.now('value') > self.ema_slow.now('value'):
            self.buy_order = self.market_order(inst_id=bar.inst_id, action=Buy, qty=self.qty)
            logger.info("%s,B,%s,%s,%.2f,%.2f,%.2f" % (
                bar.timestamp, self.buy_order.cl_id, self.buy_order.cl_ord_id, bar.close, self.ema_fast.now('value'),
                self.ema_slow.now('value')))
        elif self.buy_order is not None and self.ema_fast.now('value') < self.ema_slow.now('value'):
            sell_order = self.market_order(inst_id=bar.inst_id, action=Sell, qty=self.qty)
            logger.info("%s,S,%s,%s,%.2f,%.2f,%.2f" % (
                bar.timestamp, sell_order.cl_id, sell_order.cl_ord_id, bar.close, self.ema_fast.now('value'),
                self.ema_slow.now('value')))
