from swigibpy import Contract, Order, TagValue, TagValueList

from algotrader.event.order import *
from algotrader.provider.broker.ib.ib_broker import IBBroker

from algotrader.event.market_data import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

import swigibpy

class IBModelFactory:

    IB_DATETIME_FORMAT = "%Y%m%d %H:%M:%S %Z"

    sec_type_mapping = {
    }

    ccy_mapping = {
    }

    ord_action_mapping = {
        OrdAction.BUY: "BUY",
        OrdAction.SELL: "SELL",
        OrdAction.SSHORT: "SSHORT"
    }

    ord_type_mapping = {
        OrdType.MARKET: "MKT",
        OrdType.LIMIT: "LMT",
        OrdType.STOP: "STP",
        OrdType.STOP_LIMIT: "STPLMT",
        OrdType.MARKET_ON_CLOSE: "MOC",
        OrdType.LIMIT_ON_CLOSE: "LOC",
        OrdType.TRAILING_STOP: "TRAIL",
        OrdType.MARKET_TO_LIMIT: "MTL",
        OrdType.MARKET_IF_PRICE_TOUCHED: "MIT",
        OrdType.MARKET_ON_OPEN: "MOO"
    }

    tif_mapping = {
        TIF.DAY: "DAY",
        TIF.GTC: "GTC",
        TIF.FOK: "FOK",
        TIF.GTD: "GTD"
    }

    hist_data_type_mapping = {
        Bar : "TRADES",
        Quote : "BID_ASK",
        Trade : "TRADES"
    }

    bar_size_mapping = {
        BarSize.S1 : "1 secs",
        BarSize.S5 : "5 secs",
        BarSize.S15 : "15 secs",
        BarSize.S30 : "30 secs",
        BarSize.M1 : "1 min",
        BarSize.M2 : "2 mins",
        BarSize.M5 : "5 mins",
        BarSize.M15 : "15 mins",
        BarSize.M30 : "30 mins",
        BarSize.H1 : "1 hour",
        BarSize.D1 : "1 day",

    }


    ib_md_operation_map = {
        0 : MDOperation.Insert,
        1 : MDOperation.Update,
        2 : MDOperation.Delete
    }


    ib_md_side_map = {
        0 : MDSide.Ask,
        1 : MDSide.Bid
    }

    ib_ord_status_map = {
        "Submitted" : OrdStatus.NEW,
        "PendingCancel" : OrdStatus.PENDING_CANCEL,
        "Cancelled" : OrdStatus.CANCELLED,
        "Inactive" : OrdStatus.REJECTED

    }

    def __init__(self, ref_data_mgr):
        self.__ref_data_mgr = ref_data_mgr

    def create_ib_order(self, order):

        # Order details
        algoParams = TagValueList()

        if order.params:
            for k, v in order.params.items():
                algoParams.append(TagValue(k, v))

        ib_order = Order()
        ib_order.action = self.convert_ord_action(order.action)
        ib_order.lmtPrice = order.limit_price
        ib_order.orderType = self.convert_ord_type(order.type)
        ib_order.totalQuantity = self.qty
        ib_order.tif = self.convert_tif(order.tif)

        ## TODO set algo strategy from Order to IBOrder
        # ib_order.algoStrategy = "AD"
        # ib_order.algoParams = algoParams

        ## TODO double check
        if order.oca_tag :
            ib_order.ocaGroup = order.oca_tag
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
        return self.ord_action_mapping[ord_type]

    def convert_tif(self, tif):
        return self.tif_mapping[tif]

    def convert_ord_action(self, ord_action):
        return self.ord_action_mapping[ord_action]

    def create_ib_contract(self, inst_id):
        inst = self.__ref_data_mgr.get_inst(inst_id=inst_id)

        contract = Contract()
        contract.exchange = inst.get_exch_id(IBBroker.ID)
        contract.symbol = inst.get_symbol(IBBroker.ID)
        contract.secType = self.convert_sec_type(inst.type)
        contract.currency = self.convert_sec_type(inst.ccy_id)
        pass


    def convert_hist_data_type(self, type):
        return self.hist_data_type_mapping.get(type, "MIDPOINT")


    def convert_datetime(self, datetime):
        return datetime.strftime(self.IB_DATETIME_FORMAT)


    def convert_ib_datetime(self, ib_datetime_str):
        return datetime.strptime(self.IB_DATETIME_FORMAT, ib_datetime_str)


    def convert_time_period(self, start_time, end_time):
        diff = relativedelta(start_time, end_time)
        if diff.years:
            if diff.months and diff.months >=11:
                return "%s Y" % (diff.years + 1)
            return "%s Y" % diff.years
        elif diff.months:
            if diff.days and diff.days >=27:
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
        return self.ib_ord_status_map.get(ib_ord_status, OrdStatus.UNKNOWN)