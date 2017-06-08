from algotrader.event.order import OrdAction
from algotrader.strategy.strategy import Strategy
from algotrader.technical.roc import ROC
from algotrader.technical.pipeline.pairwise import PairCorrelation
from algotrader.technical.pipeline.make_vector import MakeVector
from algotrader.technical.pipeline.rank import Rank
from algotrader.utils import logger
import numpy as np


class AlphaFormula3(Strategy):
    def __init__(self, stg_id=None, stg_configs=None):
        super(AlphaFormula3, self).__init__(stg_id=stg_id, stg_configs=stg_configs)
        self.day_count = 0
        self.order = None

    def _start(self, app_context, **kwargs):
        self.length = self.get_stg_config_value("length", 10)

        self.bars = [self.app_context.inst_data_mgr.get_series(
            "Bar.%s.Time.300" % i) for i in self.app_context.app_config.instrument_ids]

        for bar in self.bars:
            bar.start(app_context)

        self.opens = MakeVector(self.bars, input_key='Open')
        self.volumes = MakeVector(self.bars, input_key="Volume")
        self.rank_opens = Rank(self.bars, input_key='open')
        self.rank_opens.start(app_context)

        self.rank_volumes = Rank(self.bars, input_key='Volume')
        self.rank_volumes.start(app_context)
        #
        self.pair_correlation = PairCorrelation(self.rank_opens, self.rank_volumes, length=self.length)
        self.pair_correlation.start(app_context)

        super(AlphaFormula3, self)._start(app_context, **kwargs)

    def _stop(self):
        super(AlphaFormula3, self)._stop()

    def on_bar(self, bar):
        # rank = self.rank_opens.now('value')
        # logger.info("[%s] %s" % (self.__class__.__name__, rank))
        # if np.all(np.isnan(rank)):
        #     return
        corr = self.pair_correlation.now('value')
        if np.any(np.isnan(corr)):
            return


        weight = [corr[i, i+2] for i in range(len(self.bars))]
        # weight = rank
        weight = -1*weight[0]

        portfolio = self.get_portfolio()
        allocation = portfolio.total_equity * weight
        delta = allocation - portfolio.stock_value

        index = self.app_context.app_config.instrument_ids.index(bar.inst_id)
        qty = delta[index]
        # logger.info("%s,B,%.2f" % (bar.timestamp, bar.close))
        self.order = self.market_order(inst_id=bar.inst_id, action=OrdAction.BUY, qty=qty) if qty > 0 else \
            self.market_order(inst_id=bar.inst_id, action=OrdAction.SELL, qty=-qty)


