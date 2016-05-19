'''
Created on 4/5/16
@author = 'jason'
'''

try:
    # Python 2 compatibility
    from Queue import Queue
except:
    from queue import Queue

from datetime import datetime

from swigibpy import (EWrapper, EPosixClientSocket)

from algotrader.event.market_data import MarketDataEventHandler
from algotrader.provider import Feed
from algotrader.provider.broker.ib.iborder_factory import makeIbOrder
from algotrader.provider.broker.ib.instrument_mgr import IBContractFactory
from algotrader.provider.provider import Broker
from algotrader.trading.ref_data import InMemoryRefDataManager
from algotrader.utils import logger


class DataRecord:
    __slots__ = (
        'inst_id',
        'bid',
        'ask',
        'last',
        'open',
        'high',
        'low',
        'close',
        'bid_size',
        'ask_size',
        'last_size',
        'vol',
        'trade_req',
        'quote_req'
    )

    def __init__(self, inst_id):
        self.inst_id = inst_id
        self.bid = 0.0
        self.ask = 0.0
        self.last = 0.0

        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0

        self.bid_size = 0
        self.ask_size = 0
        self.last_size = 0

        self.vol = 0

        self.trade_req = False
        self.quote_req = False


class SubscriptionRegistry:
    def __init__(self):
        self.subscriptions = {}
        self.data_records = {}

    def add_subscription(self, req_id, sub_key):
        self.subscriptions[req_id] = sub_key

    def get_subscription_key(self, req_id):
        return self.subscriptions.get(req_id, None)

    def get_subsciption_id(self, sub_key):
        for req_id, key in self.subscriptions.items():
            if sub_key == key:
                return req_id
        return None

    def remove_subscription(self, req_id=None, sub_key=None):
        if req_id and req_id in self.subscriptions:
            del self.subscriptions[req_id]
            return True
        elif sub_key:
            sub_id = self.get_subsciption_id(sub_key)
            return self.remove_subscription(req_id=req_id)
        else:
            return False

    def has_subscription(self, req_id=None, sub_key=None):
        if req_id:
            return req_id in self.subscriptions
        if sub_key and self.get_subsciption_id(sub_key):
            return True
        return False

    def clear(self):
        self.subscriptions.clear()
        self.data_records.clear()


class OrderRegistry:
    def ___init__(self):
        self.__clordid__order_dict = {}
        self.__ordid_clordid_dict = {}

    def add_order(self, order):
        self.__clordid__order_dict[order.cl_ord_id] = order
        self.__ordid_clordid_dict[order.ord_id] = order.cl_ord_id

    def remove_order(self, order):
        del self.__clordid__order_dict[order.cl_ord_id]
        del self.__ordid_clordid_dict[order.ord_id]

    def get_order(self, ord_id=None, cl_ord_id=None):
        if ord_id and not cl_ord_id:
            cl_ord_id = self.__ordid_clordid_dict[ord_id]

        if cl_ord_id:
            return self.__clordid__order_dict[cl_ord_id]

    def get_ord_id(self, cl_ord_id):
        if cl_ord_id in self.__clordid__order_dict:
            return self.__clordid__order_dict[cl_ord_id].ord_id
        return None


import time
from .ib_model_factory import IBModelFactory


class IBBroker(Broker, EWrapper, MarketDataEventHandler, Feed):
    ID = "IB"

    def __init__(self, port=4001, client_id=12, ref_data_mgr=None):
        self.__tws = EPosixClientSocket(self)
        self.__port = port
        self.__client_id = client_id
        self.__ref_data_mgr = ref_data_mgr if ref_data_mgr else InMemoryRefDataManager()
        self.__model_factory = IBModelFactory(self.__ref_data_mgr)
        self.__data_sub_reg = SubscriptionRegistry()
        self.__ord_reg = OrderRegistry()
        self.__next_request_id = 1
        self.__next_order_id = Queue()
        self.__contract_factory = IBContractFactory(self.__instru_mgr)

    def start(self):
        if not self.__tws.eConnect("", self.__port, self.__client_id):
            raise RuntimeError('Failed to connect TWS')

        # wait until we get the next_order_id
        while (self.__next_order_id.empty()):
            time.sleep(1)

    def stop(self):
        self.__tws.eDisconnect()
        ## todo unsubscribe market data
        ## cancel order !?

    def __del__(self):
        self.stop()

    def id(self):
        return IBBroker.ID

    def __next_request_id(self):
        req_id = self.__next_request_id
        self.__next_request_id += 1
        return req_id

    def __next_order_id(self):
        """get from next_order_id, increment and set the value back to next_order_id, """
        order_id = self.__next_order_id.get()
        next_order_id = order_id + 1
        self.__next_order_id.put(next_order_id)
        return order_id

    def subscribe_mktdata(self, sub_key):
        if not self.__data_sub_reg.has_subscription(sub_key=sub_key):
            req_id = self.__next_request_id()
            self.__data_sub_reg.add_subscription(req_id, sub_key)
            contract = self.__model_factory.create_ib_contract(sub_key.inst_id)
            self.__tws.reqMktData(req_id, contract, '', False)

    def unsubscribe_mktdata(self, sub_key):
        req_id = self.__data_sub_reg.get_subsciption_id(sub_key)

        if req_id and self.__data_sub_reg.remove_subscription(req_id):
            self.__tws.cancelMktData(req_id)

    def subscribe_hist_data(self, sub_key):
        if not self.__data_sub_reg.has_subscription(sub_key=sub_key):
            req_id = self.__next_request_id()
            self.__data_sub_reg.add_subscription(req_id, sub_key)
            contract = self.__model_factory.create_ib_contract(sub_key.inst_id)
            endDate = datetime.today()
            # TODO
            self.__tws.reqHistoricalData(req_id, contract,
                                         endDate.strftime("%Y%m%d %H:%M:%S %Z"),  # endDateTime,
                                         "1 W",  # durationStr,
                                         "1 day",  # barSizeSetting,
                                         "TRADES",  # whatToShow,
                                         0,  # useRTH,
                                         1  # formatDate
                                         )

    def unsubscribe_hist_data(self, sub_key):
        req_id = self.__data_sub_reg.get_subsciption_id(sub_key)

        if req_id and self.__data_sub_reg.remove_subscription(req_id):
            self.__tws.cancelHistoricalData(req_id)

    def request_fa(self):
        self.__tws.requestFA(1)  # groups
        self.__tws.requestFA(2)  # profile
        self.__tws.requestFA(3)  # account_aliases

    def on_order(self, order):
        logger.debug("[%s] %s" % (self.__class__.__name__, order))

        order.ord_id = self.__next_order_id()
        self.__ord_reg.add_order(order)

        ib_order = self.__model_factory.create_ib_order(order)
        contract = self.__model_factory.create_ib_contract(order.instrument)

        # TODO what is this??
        # self.__callback.on_order(
        #     order)  # let the callback class has a reference to the order so that once the IB return the exeuction report we can undate the order accordingly

        self.__tws.placeOrder(order.ord_id, contract, ib_order)


    def on_ord_update_req(self, order):
        existing_order = self.__ord_reg.get_order(cl_ord_id=order.cl_ord_id)
        if existing_order and existing_order.ord_id:
            order.ord_id = existing_order.ord_id

            self.__ord_reg.add_order(order)

            ib_order = self.__model_factory.create_ib_order(order)
            contract = self.__model_factory.create_ib_contract(order.instrument)
            self.__tws.placeOrder(order.ord_id, contract, ib_order)
        else:
            print "cannot find old order, cl_ord_id = %s" % order.cl_ord_id


    def on_ord_cancel_req(self, order):
        ord_id = order.ord_id
        if not ord_id:
            ord_id = self.__ord_reg.get_ord_id(order.cl_ord_id)

        if ord_id:
            self.__tws.cancelOrder(ord_id)
        else:
            print "cannot find old order, ord_id = %s, cl_ord_id = %s" % (order.ord_id, order.cl_ord_id)

    def req_open_orders(self):
        self.__tws.reqOpenOrders()

    def req_mkt_depth(self, market_orderbook_numdepth=5):
        for id, row in self.__instru_mgr.instrument_repo.iterrows():
            self.__tws.reqMktDepth(id, self.__contract_factory.buildStockOrCashContract(row['symbol']),
                                   market_orderbook_numdepth)

    def cancel_mkt_depth(self, *args, **kwargs):
        for id, row in self.__instru_mgr.instrument_repo.iterrows():
            self.__tws.cancelMktDepth(id)

    ### EWrapper

    def nextValidId(self, orderId):
        """
        OrderId orderId
        """
        if self.__next_order_id.empty() or orderId > self.__next_order_id.get():
            self.__next_order_id.put(orderId)

    def contractDetails(self, reqId, contractDetails):
        """
        int reqId, ContractDetails contractDetails
        """
        pass

    def contractDetailsEnd(self, reqId):
        pass

    def bondContractDetails(self, reqId, contractDetails):
        """
        int reqId, ContractDetails contractDetails
        """
        pass

    def error(self, id, errorCode, errorString):
        pass

    def tickPrice(self, tickerId, field, price, canAutoExecute):
        """
        TickerId tickerId, TickType field, double price, int canAutoExecute
        """
        pass

    def tickSize(self, tickerId, field, size):
        """
        TickerId tickerId, TickType field, int size
        """
        pass

    def tickOptionComputation(self, tickerId, tickType, impliedVol, delta, optPrice, gamma, vega, theta, undPrice):
        """
        TickerId tickerId, TickType tickType, double impliedVol, double delta, double optPrice,
        double pvDividend, double gamma, double vega, double theta, double undPrice
        """
        pass

    def tickGeneric(self, tickerId, tickType, value):
        """
        TickerId tickerId, TickType tickType, double value
        """
        pass

    def tickString(self, tickerId, tickType, value):
        """
        TickerId tickerId, TickType tickType, IBString const & value
        """
        pass

    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, totalDividends, holdDays, futureExpiry,
                dividendImpact, dividendsToExpiry):
        """
        EWrapper self, TickerId tickerId, TickType tickType, double basisPoints, IBString const & formattedBasisPoints,
                                                                                                      double totalDividends, int holdDays, IBString const & futureExpiry,
                                                                                                                                                    double dividendImpact, double dividendsToExpiry
        """
        pass

    def updateAccountValue(self, key, val, currency, accountName):
        """
        IBString const & key, IBString const & val, IBString const & currency, IBString const & accountName
        """
        pass

    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL,
                        accountName):
        """
        Contract contract, int position, double marketPrice, double marketValue, double averageCost,
        double unrealizedPNL, double realizedPNL, IBString const & accountName
        """
        pass

    def updateAccountTime(self, timeStamp):
        """
        IBString const & timeStamp
        """
        pass

    def accountDownloadEnd(self, accountName):
        """
        IBString const & accountName
        """
        pass

    def updateMktDepth(self, id, position, operation, side, price, size):
        """
        TickerId id, int position, int operation, int side, double price, int size
        """
        pass

    def updateMktDepthL2(self, id, position, marketMaker, operation, side, price, size):
        """
        TickerId id, int position, IBString marketMaker, int operation, int side, double price,
        int size
        """
        pass

    def historicalData(self, reqId, date, open, high,
                       low, close, volume,
                       barCount, WAP, hasGaps):
        """
        TickerId reqId, IBString const & date, double open, double high, double low, double close,
        int volume, int barCount, double WAP, int hasGaps)
        """
        pass

    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        """
        TickerId reqId, long time, double open, double high, double low, double close, long volume,
        double wap, int count
        """
        pass

    def currentTime(self, time):
        """
        long time
        """
        pass

    def orderStatus(self, id, status, filled, remaining, avgFillPrice, permId,
                    parentId, lastFilledPrice, clientId, whyHeld):
        """
        OrderId orderId, IBString const & status, int filled, int remaining, double avgFillPrice,
        int permId, int parentId, double lastFillPrice, int clientId, IBString const & whyHeld
        """
        pass

    def openOrderEnd(self):
        pass

    def execDetails(self, reqId, contract, execution):
        """
        int reqId, Contract contract, Execution execution
        """
        pass

    def execDetailsEnd(self, reqId):
        """
        int reqId
        """
        pass

    def managedAccounts(self, accountsList):
        """
        IBString const & accountsList
        """
        pass

    def connectionClosed(self):
        pass

    def openOrder(self, orderID, contract, order, orderState):
        """
        OrderId orderId, Contract arg0, Order arg1, OrderState arg2
        """
        pass

    def commissionReport(self, commissionReport):
        """
        CommissionReport commissionReport
        """
        pass

    def scannerParameters(self, xml):
        """
        IBString const & xml
        """
        pass

    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        """
        int reqId, int rank, ContractDetails contractDetails, IBString const & distance,
        IBString const & benchmark, IBString const & projection, IBString const & legsStr
        """
        pass

    def scannerDataEnd(self, reqId):
        """
        int reqId
        """
        pass

    def fundamentalData(self, reqId, data):
        """
        TickerId reqId, IBString const & data
        """
        pass

    def deltaNeutralValidation(self, reqId, underComp):
        """
        int reqId, UnderComp underComp
        """
        pass

    def marketDataType(self, reqId, marketDataType):
        """
        TickerId reqId, int marketDataType
        """
        pass

    def tickSnapshotEnd(self, reqId):
        """
        int reqId
        """
        pass

    def updateNewsBulletin(self, msgId, msgType, newsMessage, originExch):
        """
        int msgId, int msgType, IBString const & newsMessage, IBString const & originExch
        """
        pass

    def receiveFA(self, pFaDataType, cxml):
        """
        faDataType pFaDataType, IBString const & cxml
        """
        pass



        # def on_bar(self, bar):
        # self.__process_event(bar)

        # def on_quote(self, quote):
        # self.__process_event(quote)

        # def on_trade(self, trade):
        # self.__process_event(trade)

        # def __process_event(self, event):
        #     logger.debug("[%s] %s" % (self.__class__.__name__, event))
        #     if event.instrument in self.__order_map:
        #         for order in self.__order_map[event.instrument].values():
        #             fill_info = self.__fill_strategy.process_w_market_data(order, event, False)
        #             executed = self.execute(order, fill_info)




        # def on_order(self, order):
        #     logger.debug("[%s] %s" % (self.__class__.__name__, order))
        #
        #     self.__add_order(order)
        #     # self.__send_exec_report(order, 0, 0, OrdStatus.SUBMITTED)
        #
        #     # self.__tws.placeOrder(self.next_exec_id(), order.instrument)
        #     # fill_info = self.__fill_strategy.process_new_order(order)
        #     # executed = self.execute(order, fill_info)
        #
        # def __add_order(self, order):
        #     orders = self.__order_map[order.instrument]
        #     orders[order.ord_id] = order
        #
        # def __remove_order(self, order):
        #     if order.instrument in self.__order_map:
        #         orders = self.__order_map[order.instrument]
        #         if order.ord_id in orders:
        #             del orders[order.ord_id]
        #
        # def execute(self, order, fill_info):
        #     if not fill_info or fill_info.fill_price <= 0 or fill_info.fill_price <= 0:
        #         return False
        #
        #     filled_price = fill_info.fill_price
        #     filled_qty = fill_info.fill_qty
        #
        #     if order.is_done():
        #         self.__remove_order(order)
        #         return False
        #
        #     if filled_qty < order.leave_qty():
        #         self.__send_exec_report(order, filled_price, filled_qty, OrdStatus.PARTIALLY_FILLED)
        #         return False
        #     else:
        #         filled_qty = order.leave_qty()
        #         self.__send_exec_report(order, filled_price, filled_qty, OrdStatus.FILLED)
        #         self.__remove_order(order)
        #         return True
        #
        # def __send_status(self, order, ord_status):
        #     ord_update = OrderStatusUpdate(broker_id=IbCallback.ID, ord_id=order.ord_id, instrument=order.instrument,
        #                                    timestamp=clock.default_clock.current_date_time(), status=ord_status)
        #     self.__exec__handler.on_ord_upd(ord_update)
        #
        # def __send_exec_report(self, order, filled_price, filled_qty, ord_status):
        #     commission = self.__commission.calc(order, filled_price, filled_qty)
        #     exec_report = ExecutionReport(broker_id=IbCallback.ID, ord_id=order.ord_id, instrument=order.instrument,
        #                                   timestamp=clock.default_clock.current_date_time(), er_id=self.next_exec_id(),
        #                                   filled_qty=filled_qty,
        #                                   filled_price=filled_price, status=ord_status,
        #                                   commission=commission)
        #
        #     self.__exec__handler.on_exec_report(exec_report)
        #
        # def _get_orders(self):
        #     return self.__order_map
