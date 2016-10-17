from algotrader.event.order import OrdAction
from algotrader.strategy.strategy import Strategy
from algotrader.technical.ma import SMA
from algotrader.utils import logger


class SMAStrategy(Strategy):
    def __init__(self, stg_id=None, trading_config=None):
        super(SMAStrategy, self).__init__(stg_id=stg_id, trading_config=trading_config)
        self.buy_order = None

    def _start(self, app_context, **kwargs):
        self.qty = self.get_config_value("qty", 1)
        self.bar = app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % self.trading_config.instrument_ids[0])

        self.sma_fast = SMA(self.bar, 'close', 10)
        self.sma_fast.start(app_context)

        self.sma_slow = SMA(self.bar, 'close', 25)
        self.sma_slow.start(app_context)

        super(SMAStrategy, self)._start(app_context, **kwargs)

    def _stop(self):
        super(SMAStrategy, self)._stop()

    def on_bar(self, bar):
        if self.buy_order is None and self.sma_fast.now('value') > self.sma_slow.now('value'):
            self.buy_order = self.market_order(inst_id=bar.inst_id, action=OrdAction.BUY, qty=self.qty)
            logger.info("%s,B,%s,%s,%.2f,%.2f,%.2f" % (
                bar.timestamp, self.buy_order.cl_id, self.buy_order.cl_ord_id, bar.close, self.sma_fast.now('value'),
                self.sma_slow.now('value')))
        elif self.buy_order is not None and self.sma_fast.now('value') < self.sma_slow.now('value'):
            sell_order = self.market_order(inst_id=bar.inst_id, action=OrdAction.SELL, qty=self.qty)
            logger.info("%s,S,%s,%s,%.2f,%.2f,%.2f" % (
                bar.timestamp, sell_order.cl_id, sell_order.cl_ord_id, bar.close, self.sma_fast.now('value'),
                self.sma_slow.now('value')))
            self.buy_order = None
