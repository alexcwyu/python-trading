from datetime import datetime

import swigibpy
from dateutil.relativedelta import relativedelta

from algotrader.model.trade_data_pb2 import *
from algotrader.model.market_data_pb2 import MarketDepth
from algotrader.provider.broker import Broker
from algotrader.utils.market_data import MarketDataSubscriptionRequest, S1, S5, S15, S30, M1, M5, M15, M30, H1, D1
from algotrader.utils.date import datetime_to_unixtimemillis


class IBModelFactory:
    IB_DATETIME_FORMAT = "%Y%m%d %H:%M:%S %Z"
    IB_DATETIME_FORMAT2 = "%Y%m%d %H:%M:%S"
    IB_DATE_FORMAT = "%Y%m%d"

    sec_type_mapping = {
    }

    ccy_mapping = {
    }

    ord_action_mapping = {
        Buy: "BUY",
        Sell: "SELL",
        # OrderAction.SSHORT: "SSHORT"
    }

    ord_type_mapping = {
        Market: "MKT",
        Limit: "LMT",
        Stop: "STP",
        StopLimit: "STPLMT",
        MarketOnClose: "MOC",
        LimitOnClose: "LOC",
        TrailingStop: "TRAIL",
        MarketToLimit: "MTL",
        MarketIfPriceTouched: "MIT",
        MarketOnOpen: "MOO"
    }

    tif_mapping = {
        DAY: "DAY",
        GTC: "GTC",
        FOK: "FOK",
        GTD: "GTD"
    }

    hist_data_type_mapping = {
        MarketDataSubscriptionRequest.Bar: "TRADES",
        MarketDataSubscriptionRequest.Quote: "BID_ASK",
        MarketDataSubscriptionRequest.Trade: "TRADES"
    }

    bar_size_mapping = {
        S1: "1 secs",
        S5: "5 secs",
        S15: "15 secs",
        S30: "30 secs",
        M1: "1 min",
        M5: "5 mins",
        M15: "15 mins",
        M30: "30 mins",
        H1: "1 hour",
        D1: "1 day",

    }

    ib_md_operation_map = {
        0: MarketDepth.Insert,
        1: MarketDepth.Update,
        2: MarketDepth.Delete
    }

    ib_md_side_map = {
        0: MarketDepth.Ask,
        1: MarketDepth.Bid
    }

    ib_ord_status_map = {
        "Submitted": New,
        "PendingCancel": PendingCancel,
        "Cancelled": Cancelled,
        "Inactive": Rejected

    }

    def __init__(self, ref_data_mgr):
        self.__ref_data_mgr = ref_data_mgr

    def create_ib_order(self, new_ord_req):

        # Order details
        algoParams = swigibpy.TagValueList()

        if new_ord_req.params:
            for k, v in new_ord_req.params.items():
                algoParams.append(swigibpy.TagValue(k, v))

        ib_order = swigibpy.Order()
        ib_order.action = self.convert_ord_action(new_ord_req.action)
        ib_order.lmtPrice = new_ord_req.limit_price
        ib_order.orderType = self.convert_ord_type(new_ord_req.type)
        ib_order.totalQuantity = new_ord_req.qty
        ib_order.tif = self.convert_tif(new_ord_req.tif)

        ## TODO set algo strategy from Order to IBOrder
        # ib_order.algoStrategy = "AD"
        # ib_order.algoParams = algoParams

        ## TODO double check
        if new_ord_req.oca_tag:
            ib_order.ocaGroup = new_ord_req.oca_tag
        return ib_order

    def convert_sec_type(self, inst_type):
        if inst_type in self.sec_type_mapping:
            return self.sec_type_mapping[inst_type]
        return inst_type

    def convert_ccy(self, ccy):
        if ccy in self.ccy_mapping:
            return self.ccy_mapping[ccy]
        return ccy

    def convert_ord_type(self, ord_type):
        return self.ord_type_mapping[ord_type]

    def convert_tif(self, tif):
        return self.tif_mapping[tif]

    def convert_ord_action(self, ord_action):
        return self.ord_action_mapping[ord_action]

    def create_ib_contract(self, inst_id=None, symbol=None, exchange=None, sec_type=None, currency=None,
                           include_expired=False):
        contract = swigibpy.Contract()

        if inst_id:
            inst = self.__ref_data_mgr.get_inst(inst_id=inst_id)
            contract.exchange = inst.get_exch_id(Broker.IB)
            contract.symbol = inst.get_symbol(Broker.IB)
            contract.secType = self.convert_sec_type(inst.type)
            contract.currency = self.convert_ccy(inst.ccy_id)
        else:
            if exchange:
                contract.exchange = exchange
            if symbol:
                contract.symbol = symbol
            if sec_type:
                contract.secType = sec_type
            if currency:
                contract.currency = currency

        if include_expired:
            contract.includeExpired = include_expired

        return contract

    def create_ib_scanner_subsciption(self, num_row=None, inst_type=None, location_code=None, scan_code=None,
                                      above_price=None, below_price=None, above_vol=None, avg_opt_vol_above=None,
                                      mkt_cap_above=None, mkt_cap_below=None, moody_rating_above=None,
                                      moody_rating_below=None,
                                      sp_rating_above=None, sp_rating_below=None, mat_date_above=None,
                                      mat_date_below=None,
                                      coupon_rate_above=None, coupon_rate_below=None, exc_convertible=None,
                                      scanner_setting_pairs=None,
                                      stk_type_filter=None):

        sub = swigibpy.ScannerSubscription()

        if num_row is not None:
            sub.numberOfRows = num_row
        if inst_type is not None:
            sub.instrument = inst_type
        if location_code is not None:
            sub.locationCode = location_code
        if scan_code is not None:
            sub.scanCode = scan_code
        if above_price is not None:
            sub.abovePrice = above_price
        if below_price is not None:
            sub.belowPrice = below_price
        if above_vol is not None:
            sub.aboveVolume = above_vol
        if avg_opt_vol_above is not None:
            sub.averageOptionVolumeAbove = avg_opt_vol_above
        if mkt_cap_above is not None:
            sub.marketCapAbove = mkt_cap_above
        if mkt_cap_below is not None:
            sub.marketCapBelow = mkt_cap_below
        if moody_rating_above is not None:
            sub.moodyRatingAbove = moody_rating_above
        if moody_rating_below is not None:
            sub.moodyRatingBelow = moody_rating_below
        if sp_rating_above is not None:
            sub.spRatingAbove = sp_rating_above
        if sp_rating_below is not None:
            sub.spRatingBelow = sp_rating_below
        if mat_date_above is not None:
            sub.maturityDateAbove = mat_date_above
        if mat_date_below is not None:
            sub.maturityDateBelow = mat_date_below
        if coupon_rate_above is not None:
            sub.couponRateAbove = coupon_rate_above
        if coupon_rate_below is not None:
            sub.couponRateBelow = coupon_rate_below
        if exc_convertible is not None:
            sub.excludeConvertible = exc_convertible
        if scanner_setting_pairs is not None:
            sub.scannerSettingPairs = scanner_setting_pairs
        if stk_type_filter is not None:
            sub.stockTypeFilter = stk_type_filter

        return sub

    def convert_hist_data_type(self, type):
        return self.hist_data_type_mapping.get(type, "MIDPOINT")

    def convert_datetime(self, dt):
        return dt.strftime(self.IB_DATETIME_FORMAT)

    def convert_ib_date(self, ib_date_str):
        return datetime_to_unixtimemillis(datetime.strptime(ib_date_str, self.IB_DATE_FORMAT))

    def convert_ib_datetime(self, ib_datetime_str):
        return datetime_to_unixtimemillis(datetime.strptime(ib_datetime_str, self.IB_DATETIME_FORMAT2))

    def convert_ib_time(self, ib_time):
        return datetime_to_unixtimemillis(datetime.fromtimestamp(ib_time))

    def convert_time_period(self, start_time, end_time):
        diff = relativedelta(end_time, start_time)
        if diff.years:
            if diff.months and diff.months >= 11:
                return "%s Y" % (diff.years + 1)
            return "%s Y" % diff.years
        elif diff.months:
            if diff.days and diff.days >= 27:
                return "%s M" % (diff.months + 1)
            return "%s M" % diff.months
        elif diff.days:
            return "%s D" % diff.days
        else:
            return "1 M"

    def convert_bar_size(self, bar_size):
        return self.bar_size_mapping.get(bar_size, "5 secs")

    def convert_ib_md_operation(self, ib_md_operation):
        return self.ib_md_operation_map[ib_md_operation]

    def convert_ib_md_side(self, ib_md_side):
        return self.ib_md_side_map[ib_md_side]

    def convert_ib_ord_status(self, ib_ord_status):
        return self.ib_ord_status_map.get(ib_ord_status, OrderStatus.UNKNOWN)
