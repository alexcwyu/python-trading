"""
Created on 11/5/16
Author = jchan
"""
__author__ = 'jchan'

from collections import OrderedDict
from algotrader.event.order import OrdAction
from algotrader.strategy.strategy import Strategy
from algotrader.technical.roc import ROC
from algotrader.technical.pipeline import PipeLine
from algotrader.technical.pipeline.pairwise import PairCorrelation
from algotrader.technical.pipeline.make_vector import MakeVector
from algotrader.technical.pipeline.rank import Rank
from algotrader.technical.pipeline.cross_sessional_apply import Delta, Log
from algotrader.technical.pipeline.pairwise import Minus, Divides
from algotrader.utils import logger
from algotrader.utils.date_utils import DateUtils
import numpy as np

class VIXFuture(Strategy):
    def __init__(self, stg_id=None, stg_configs=None):
        super(VIXFuture, self).__init__(stg_id=stg_id, stg_configs=stg_configs)
        self.day_count = 0
        self.order = None
        self.exp_date_lb = None
        self.exp_date_ub = None
        self.qty = 1
        self.bar_repo = {}
        self.vix_index = None
        self.qty = None
        self.exp_date_lb = None
        self.exp_date_ub = None

    def _start(self, app_context, **kwargs):
        self.qty = self.get_stg_config_value("qty", 10)
        self.exp_date_lb = self.get_stg_config_value("exp_date_lb", 5)
        self.exp_date_ub = self.get_stg_config_value("exp_date_ub", 180)
        # self.contracts = self.get_stg_config_value("contracts", [])
        # logger.debug("[%s] contract %s" % (self.__class__.__name__, self.contracts))

        # self.bars = [self.app_context.inst_data_mgr.get_series(
        #     "Bar.%s.Time.300" % i) for i in self.app_context.app_config.instrument_ids if i in self.contracts]

        self.bar_repo = {i: self.app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % i)
                         for i in self.app_context.app_config.instrument_ids}

        # for bar in self.bars:
        for bar in self.bar_repo.values():
            bar.start(app_context)


        self.vix_index = self.app_context.inst_data_mgr.get_inst(symbol='VIX')
        self.vix_index.start(app_context)

        # self.trading_mode = "contango"

        # self.ts = MakeVector(self.bars, input_key='close')
        # self.ts.start(app_context)

        # if not self.app_context.inst_data_mgr.has_series(self.ts.name) :
        #     self.app_context.inst_data_mgr.add_series(self.ts, raise_if_duplicate=True)
        self.hasPos = False
        self.active_futures = {}

        super(VIXFuture, self)._start(app_context, **kwargs)

    def _stop(self):
        super(VIXFuture, self)._stop()


    @staticmethod
    def future_expirydays_calculator(reval_date, instruments):
        return {i.inst_id: (i.expiry_date - reval_date).days for i in instruments}

    @staticmethod
    def daily_roll(future, index, expiry_days):
        return (future - index)/index/np.log(expiry_days)

    def on_bar(self, bar):
        reval_date = DateUtils.unixtimemillis_to_datetime(bar.timestamp)
        futures_expiry_dict = VIXFuture.future_expirydays_calculator(reval_date, self.instruments)

        active_futures = {k: v for k, v in futures_expiry_dict.iteritems()
                                if v > self.exp_date_lb and v < self.exp_date_ub}

        active_futures_sorted = OrderedDict(sorted(active_futures.items(), key=lambda y: y[1]))

        if bar.inst_id in active_futures_sorted:
            logger.debug("id is in active futures" % bar.inst_id)
            roll = VIXFuture.daily_roll(bar.adj_close, self.vix_index.now("value"), active_futures_sorted[bar.inst_id])
            logger.debug("roll = %s" % roll)
            if not self.portfolio.has_position(self.stg_id, bar.inst_id):
                threshold = self.get_stg_config_value("short_entry_threshold", 0.02)
                if roll > threshold:
                    logger.debug("Roll > threshold %s" % threshold)
                    logger.debug("Now send a short order")
                    self.market_order(inst_id=bar.inst_id, action=OrdAction.SELL, qty=self.qty)

            else:
                threshold = self.get_stg_config_value("short_exit_threshold", -0.01)
                if roll < threshold:
                    logger.debug("Roll < threshold %s" % threshold)
                    logger.debug("Now exit")
                    self.market_order(inst_id=bar.inst_id, action=OrdAction.BUY, qty=self.qty)



        #
        #
        #
        #
        #
        # # term_structure = self.ts.now('value')[0]
        # logger.info("[%s] %s" % (self.__class__.__name__, term_structure))
        #
        # if np.any(np.isnan(term_structure)):
        #     return
        #
        # if not self.hasPos:
        #     if term_structure[0] < term_structure[1]:
        #         if bar.inst_id == self.contracts[0]:
        #             self.market_order(inst_id=bar.inst_id, action=OrdAction.SELL, qty=self.qty)
        #         if bar.inst_id == self.contracts[1]:
        #             self.market_order(inst_id=bar.inst_id, action=OrdAction.BUY, qty=self.qty)
        #
        #         self.trading_mode = "contango"
        #     else:
        #         if bar.inst_id == self.contracts[0]:
        #             self.market_order(inst_id=bar.inst_id, action=OrdAction.BUY, qty=self.qty)
        #         if bar.inst_id == self.contracts[1]:
        #             self.market_order(inst_id=bar.inst_id, action=OrdAction.SELL, qty=self.qty)
        #
        #         self.trading_mode = "backwardation"
        #     self.hasPos = True
        # else:
        #     if term_structure[0] < term_structure[1] and self.trading_mode == "backwardation":
        #         if bar.inst_id == self.contracts[0]:
        #             self.market_order(inst_id=bar.inst_id, action=OrdAction.SELL, qty=2*self.qty)
        #         if bar.inst_id == self.contracts[1]:
        #             self.market_order(inst_id=bar.inst_id, action=OrdAction.BUY, qty=2*self.qty)
        #
        #         self.trading_mode = "contango"
        #     elif term_structure[0] > term_structure[1] and self.trading_mode == "contango":
        #         if bar.inst_id == self.contracts[0]:
        #             self.market_order(inst_id=bar.inst_id, action=OrdAction.BUY, qty=2*self.qty)
        #         if bar.inst_id == self.contracts[1]:
        #             self.market_order(inst_id=bar.inst_id, action=OrdAction.SELL, qty=2*self.qty)
        #
        #         self.trading_mode = "backwardation"
        #
        #
