from swigibpy import Contract, Order, TagValue, TagValueList

from algotrader.event.order import OrdAction, OrdType, TIF
from algotrader.provider.broker.ib.ib_broker import IBBroker


class IBModelFactory:
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
