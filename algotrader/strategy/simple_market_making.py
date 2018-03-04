
from algotrader import Context
from algotrader.model.trade_data_pb2 import *
from algotrader.model.market_data_pb2 import *

from algotrader.strategy import Strategy
from algotrader.technical.function_wrapper import sklearn_trasformer_function
from algotrader.technical.talib_wrapper import talib_function
from algotrader.technical.mvg_avg_force import MovingAvgForceProcess
from algotrader.utils.market_data import build_bar_frame_id, M1, D1
from algotrader.utils.logging import logger


class SimpleMarketMaking(Strategy):
    def __init__(self, stg_id: str, stg_cls: str, state: StrategyState = None):
        super(SimpleMarketMaking, self).__init__(stg_id=stg_id, stg_cls=stg_cls, state=state)
        self.qty = None
        self.tick = 1
        self.buy_order = None
        self.sell_order = None

    def _start(self, app_context, **kwargs):
        logger.info("strategy started!")
        # self.qty = self.get_stg_config_value("qty", 1)
        # self.tick = self.get_stg_config_value("tick", 1)

        self.qty = self._get_stg_config("qty", default=1)
        self.tick = self._get_stg_config("tick", default=1)

        # self.close = self.app_context.inst_data_mgr.get_series(
        #     "Bar.%s.Time.86400" % self.app_context.app_config.instrument_ids[0])
        # self.close.start(app_context)
        super(SimpleMarketMaking, self)._start(app_context, **kwargs)

    def _stop(self):
        super(SimpleMarketMaking, self)._stop()

    def on_quote(self, quote: Quote):
        # logger.info("on_quote is called with %s" % quote)
        multi = 2
        if self.buy_order is None:
            self.buy_order = self.limit_order(quote.inst_id, Buy, self.qty, quote.bid - multi * self.tick)

        if self.sell_order is None:
            self.sell_order = self.limit_order(quote.inst_id, Sell, self.qty, quote.ask + multi * self.tick)

    def on_trade(self, trade: Trade):
        logger.info("on_quote is called with %s" % trade)





