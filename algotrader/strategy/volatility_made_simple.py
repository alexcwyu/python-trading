import rx
from rx.subjects import BehaviorSubject

from algotrader.model.trade_data_pb2 import *
from algotrader.technical.talib_wrapper import EMA, SMA
from algotrader.trading.strategy import Strategy
from algotrader.utils import logger


class VixVxvRatio(Strategy):
    def __init__(self, stg_id: str, state: StrategyState = None):
        super(VixVxvRatio, self).__init__(stg_id=stg_id, state=state)
        self.day_count = 0
        self.order = None

    def _start(self, app_context, **kwargs):
        self.qty = self.get_stg_config_value("qty", 1)
        self.threshold = self.get_stg_config_value("threshold", 1)

        self.xiv = app_context.ref_data_mgr.get_inst('XIV', 'SMART')
        self.vxx = app_context.ref_data_mgr.get_inst('VXX', 'SMART')
        self.vxv = app_context.ref_data_mgr.get_inst('VXV', 'SMART')
        self.vix = app_context.ref_data_mgr.get_inst('VIX', 'SMART')  # TODO: Review index
        instruments = [self.vxx, self.xiv, self.vix]

        self.vix_bar = app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % self.vix.get_symbol())  # non tradable
        self.vxv_bar = app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % self.vxv.get_symbol())  # non tradable
        self.xiv_bar = app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % self.xiv.get_symbol())
        self.vxx_bar = app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % self.vxx.get_symbol())
        self.vix_strm = BehaviorSubject(0)
        self.vxv_strm = BehaviorSubject(0)
        self.ratio_strm = rx.Observable \
            .zip(self.vix_strm, self.vxv_strm, lambda x, y: x / y) \
            .subscribe(self.on_ratio)

        super(VixVxvRatio, self)._start(app_context, **kwargs)

    def _stop(self):
        super(VixVxvRatio, self)._stop()

    def on_bar(self, bar):
        if bar.inst_id == self.vix.id():
            self.vix_strm.on_next(bar.close)
        elif bar.inst_id == self.vxv.id():
            self.vxv_strm.on_next(bar.close)

    def on_ratio(self, ratio):
        # what is order is not filled and there is signal again?
        if self.order is None:
            # long XIV at the close when VIX index closed below the VXV index
            # long XIV when ratio < 0.92
            if ratio < self.threshold[0]:
                # logger.info("%s,B,%.2f" % (bar.timestamp, bar.close))
                self.order = self.market_order(inst_id=self.xiv.id(),
                                               action=Buy,
                                               qty=self.qty)
            # long VXX when ratio > 1.08
            elif ratio > self.threshold[1]:
                # logger.info("%s,B,%.2f" % (bar.timestamp, bar.close))
                self.order = self.market_order(inst_id=self.vxx, action=Buy, qty=self.qty)


class VxvVxmtRatio(Strategy):
    def __init__(self, stg_id=None):
        super(VxvVxmtRatio, self).__init__(stg_id=stg_id)
        self.day_count = 0
        self.order = None

    def _start(self, app_context, **kwargs):

        self.qty = self.get_stg_config_value("qty", 1)
        self.threshold = self.get_stg_config_value("threshold", 1)

        self.xiv = app_context.ref_data_mgr.get_inst('XIV', 'SMART')
        self.vxx = app_context.ref_data_mgr.get_inst('VXX', 'SMART')
        self.vxv = app_context.ref_data_mgr.get_inst('VXV', 'SMART')
        self.vxmt = app_context.ref_data_mgr.get_inst('VXMT', 'SMART')
        instruments = [self.vxx, self.xiv, self.vxmt]
        self.vix_close = app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % self.vix.get_symbol())
        self.xiv_close = app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % self.xiv.get_symbol())
        self.vxv_close = app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % self.vxv.get_symbol())
        self.vxmt_close = app_context.inst_data_mgr.get_series("Bar.%s.Time.86400" % self.vxmt.get_symbol())
        self.ema_60 = EMA()
        self.sma_fast = SMA(self.bar, 'close', 10)

        super(VxvVxmtRatio, self)._start(app_context, **kwargs)

    def on_bar(self, bar):
        ratio = self.vix_close.now('value') / self.vxv_close.now('close')
        # what is order is not filled and there is signal again?
        if self.order is None:
            # long XIV at the close when VIX index closed below the VXV index
            # long XIV when ratio < 0.92
            if ratio < self.threshold[0]:
                logger.info("%s,B,%.2f" % (bar.timestamp, bar.close))
                if bar.inst_id == self.xiv.id():
                    self.order = self.market_order(inst_id=bar.inst_id, action=Buy, qty=self.qty)

            # long VXX when ratio > 1.08
            elif ratio > self.threshold[1]:
                logger.info("%s,B,%.2f" % (bar.timestamp, bar.close))
                if bar.inst_id == self.vxx.id():
                    self.order = self.market_order(inst_id=bar.inst_id, action=Buy, qty=self.qty)
