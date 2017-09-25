import talib

from algotrader import Context
from algotrader.model.trade_data_pb2 import *
from algotrader.strategy import Strategy
from algotrader.technical.talib_wrapper import talib_function


class Down2PctStrategy(Strategy):
    def __init__(self, stg_id: str, stg_cls: str, state: StrategyState = None):
        super(Down2PctStrategy, self).__init__(stg_id=stg_id, stg_cls=stg_cls, state=state)
        self.day_count = 0
        self.order = None

    def _start(self, app_context: Context) -> None:
        self.qty = self._get_stg_config("qty", default=1)

        self.close = self.app_context.inst_data_mgr.get_series(
            "Bar.%s.close.Time.86400" % app_context.config.get_app_config("instrumentIds")[0])
        self.close.start(app_context)

        # decorate the simple function with extra attribute so that the Series as functor can retrieve
        roc_function = talib_function(periods=1, name='roc')(talib.ROC) # construct a functor
        self.roc = roc_function * self.close # close series is Functor in pymonad, see Functors in https://pypi.python.org/pypi/PyMonad/
        self.roc.start(app_context)

        super(Down2PctStrategy, self)._start(app_context)

    def _stop(self):
        super(Down2PctStrategy, self)._stop()

    def on_bar(self, bar):
        if self.order is None:
            # if self.roc.now('value') < -0.02:
            if len(self.roc) > 0 and self.roc.tail(1).data[0] < -0.02:
            # logger.info("%s,B,%.2f" % (bar.timestamp, bar.close))
                self.order = self.market_order(inst_id=bar.inst_id, action=Buy, qty=self.qty)
                self.day_count = 0
        else:
            self.day_count += 1
            if self.day_count >= 5:
                # logger.info("%s,S,%.2f" % (bar.timestamp, bar.close))
                self.market_order(inst_id=bar.inst_id, action=Sell, qty=self.qty)
                self.order = None
