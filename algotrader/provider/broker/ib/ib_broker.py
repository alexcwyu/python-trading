'''
Created on 4/5/16
@author = 'jason'
'''

import threading
import time

import swigibpy

from algotrader.event import EventBus
from algotrader.event.order import *
from algotrader.provider import Feed, broker_mgr, feed_mgr
from algotrader.provider.broker.ib.ib_model_factory import IBModelFactory
from algotrader.provider.broker.ib.ib_socket import IBSocket
from algotrader.provider.provider import Broker, HistDataSubscriptionKey, MarketDepthSubscriptionKey
from algotrader.trading.ref_data import inmemory_ref_data_mgr
from algotrader.utils import logger


class DataRecord(object):
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

    def __init__(self, inst_id, trade_req=False, quote_req=False):
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

        self.trade_req = trade_req
        self.quote_req = quote_req


class SubscriptionRegistry(object):
    def __init__(self):
        self.subscriptions = {}
        self.data_records = {}

    def add_subscription(self, req_id, sub_key):
        if req_id in self.subscriptions:
            raise "Duplicated req_id %s" % req_id

        self.subscriptions[req_id] = sub_key
        self.data_records[req_id] = DataRecord(sub_key.inst_id, quote_req=sub_key.data_type == Quote,
                                               trade_req=sub_key.data_type == Trade)

    def get_subscription_key(self, req_id):
        return self.subscriptions.get(req_id, None)

    def get_subsciption_id(self, sub_key):
        for req_id, key in self.subscriptions.items():
            if sub_key == key:
                return req_id
        return None

    def remove_subscription(self, req_id=None, sub_key=None):
        if req_id:
            if req_id in self.subscriptions:
                del self.subscriptions[req_id]
            if req_id in self.data_records:
                del self.data_records[req_id]
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

    def get_data_record(self, req_id):
        return self.data_records.get(req_id, None)

    def clear(self):
        self.subscriptions.clear()
        self.data_records.clear()


class OrderRegistry(object):
    def __init__(self):
        self.__clordid__order_dict = {}
        self.__ordid_clordid_dict = {}

    def add_order(self, order):
        self.__clordid__order_dict[order.cl_ord_id] = order
        self.__ordid_clordid_dict[order.ord_id] = order.cl_ord_id

    def remove_order(self, order):
        if order.cl_ord_id in self.__clordid__order_dict:
            del self.__clordid__order_dict[order.cl_ord_id]
        if order.ord_id in self.__ordid_clordid_dict:
            del self.__ordid_clordid_dict[order.ord_id]

    def get_order(self, ord_id=None, cl_ord_id=None):
        if ord_id and not cl_ord_id:
            cl_ord_id = self.__ordid_clordid_dict.get(ord_id, None)

        if cl_ord_id:
            return self.__clordid__order_dict.get(cl_ord_id, None)

    def get_ord_id(self, cl_ord_id):
        if cl_ord_id in self.__clordid__order_dict:
            return self.__clordid__order_dict[cl_ord_id].ord_id
        return None


class TWSPoller(threading.Thread):
    '''Continually polls TWS for any outstanding messages.

    Loops indefinitely until killed or a fatal error is encountered. Calls
    TWS's `EClientSocketBase::checkMessages` function which blocks on socket
    receive (synchronous I/O).
    '''

    def __init__(self, tws, daemon = False):
        super(TWSPoller, self).__init__()
        self.daemon = daemon
        self._tws = tws

    def run(self):
        '''Continually poll TWS'''
        ok = True
        while ok:
            ok = self._tws.checkMessages()

            if ok and (not self._tws or not self._tws.isConnected()):
                ok = False


class IBBroker(IBSocket, Broker, Feed):
    ID = "IB"

    def __init__(self, port=4001, client_id=1, account=None, ref_data_mgr=None, data_event_bus=None, execution_event_bus=None, daemon=False):
        super(IBBroker, self).__init__()

        self.__tws = swigibpy.EPosixClientSocket(self)
        self.__poller = TWSPoller(self.__tws, daemon=daemon)
        self.__port = port
        self.__client_id = client_id
        self.__account = account
        self.__ref_data_mgr = ref_data_mgr if ref_data_mgr else inmemory_ref_data_mgr
        self.__data_event_bus = data_event_bus if data_event_bus else EventBus.data_subject
        self.__execution_event_bus = execution_event_bus if execution_event_bus else EventBus.execution_subject
        self.__model_factory = IBModelFactory(self.__ref_data_mgr)
        self.__data_sub_reg = SubscriptionRegistry()
        self.__ord_reg = OrderRegistry()
        self.__next_request_id = 1
        self.__next_order_id = None
        self.__started = False

        feed_mgr.register(self)
        broker_mgr.register(self)

    def start(self):
        if not self.__started:
            self.__started = True
            if not self.__tws.eConnect("", self.__port, self.__client_id, poll_auto=False):
                raise RuntimeError('Failed to connect TWS')
            self.__poller.start()

            logger.info("Server version, %s", self.__tws.serverVersion())


            if self.__account:
                self.__req_acct_update()
            else:
                self.__tws.reqManagedAccts()

            self.__tws.reqAllOpenOrders()
            self.__tws.reqOpenOrders()

            # wait until we get the next_order_id
            while (not self.__next_order_id):
                time.sleep(1)

    def stop(self):
        self.__tws.eDisconnect()
        self.__started = False
        ## todo unsubscribe market data
        ## cancel order !?

    def __del__(self):
        self.stop()

    def id(self):
        return IBBroker.ID

    def next_request_id(self):
        req_id = self.__next_request_id
        self.__next_request_id += 1
        return req_id

    def next_order_id(self):
        """get from next_order_id, increment and set the value back to next_order_id, """
        order_id = self.__next_order_id
        self.__next_order_id += 1
        return order_id

    def subscribe_mktdata(self, sub_key):
        if isinstance(sub_key, MarketDepthSubscriptionKey):
            req_func = self.__req_market_depth
        elif isinstance(sub_key, HistDataSubscriptionKey):
            req_func = self.__req_hist_data
        elif sub_key.data_type == Bar:
            req_func = self.__req_real_time_bar
        elif sub_key.data_type == Quote or sub_key.data_type == Trade:
            req_func = self.__req_mktdata

        if req_func and not self.__data_sub_reg.has_subscription(sub_key=sub_key):
            req_id = self.next_request_id()
            self.__data_sub_reg.add_subscription(req_id, sub_key)
            contract = self.__model_factory.create_ib_contract(sub_key.inst_id)

            req_func(req_id, sub_key, contract)

    def unsubscribe_mktdata(self, sub_key):

        if isinstance(sub_key, MarketDepthSubscriptionKey):
            cancel_func = self.__cancel_market_depth
        elif isinstance(sub_key, HistDataSubscriptionKey):
            cancel_func = self.__cancel_hist_data
        elif sub_key.data_type == Bar:
            cancel_func = self.__cancel_real_time_bar
        elif sub_key.data_type == Quote or sub_key.data_type == Trade:
            cancel_func = self.__cancel_mktdata

        if cancel_func:
            req_id = self.__data_sub_reg.get_subsciption_id(sub_key)
            if req_id and self.__data_sub_reg.remove_subscription(req_id):
                cancel_func(req_id)

    def __req_mktdata(self, req_id, sub_key, contract):
        self.__tws.reqMktData(req_id, contract,
                              '',  # genericTicks
                              False  # snapshot
                              )

    def __cancel_mktdata(self, req_id):
        self.__tws.cancelMktData(req_id)

    def __req_real_time_bar(self, req_id, sub_key, contract):
        self.__tws.reqRealTimeBars(req_id, contract,
                                   sub_key.bar_size,  # barSizeSetting,
                                   self.__model_factory.convert_hist_data_type(sub_key.data_type),
                                   0  # RTH Regular trading hour
                                   )

    def __cancel_real_time_bar(self, req_id):
        self.__tws.cancelRealTimeBars(req_id)

    def __req_market_depth(self, req_id, sub_key, contract):
        self.__tws.reqMktDepth(req_id, contract, sub_key.num_rows)

    def __cancel_market_depth(self, req_id):
        self.__tws.cancelMktDepth(req_id)

    def __req_hist_data(self, req_id, sub_key, contract):
        self.__tws.reqHistoricalData(req_id, contract,
                                     self.__model_factory.convert_datetime(sub_key.to_date),  # endDateTime,
                                     self.__model_factory.convert_time_period(sub_key.from_date, sub_key.to_date),
                                     # durationStr,
                                     self.__model_factory.convert_bar_size(sub_key.bar_size),  # barSizeSetting,
                                     self.__model_factory.convert_hist_data_type(sub_key.data_type),  # whatToShow,
                                     0,  # useRTH,
                                     1  # formatDate
                                     )

    def __cancel_hist_data(self, req_id):
        self.__tws.cancelHistoricalData(req_id)

    def __request_fa(self):
        self.__tws.requestFA(1)  # groups
        self.__tws.requestFA(2)  # profile
        self.__tws.requestFA(3)  # account_aliases

    def __req_acct_update(self):
        self.__tws.reqAccountUpdates(True, self.__account)

    def on_order(self, order):
        logger.debug("[%s] %s" % (self.__class__.__name__, order))

        order.ord_id = self.next_order_id()
        self.__ord_reg.add_order(order)

        ib_order = self.__model_factory.create_ib_order(order)
        contract = self.__model_factory.create_ib_contract(order.instrument)

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
            logger.error("cannot find old order, cl_ord_id = %s" % order.cl_ord_id)

    def on_ord_cancel_req(self, order):
        ord_id = order.ord_id
        if not ord_id:
            ord_id = self.__ord_reg.get_ord_id(order.cl_ord_id)

        if ord_id:
            self.__tws.cancelOrder(ord_id)
        else:
            logger.error("cannot find old order, ord_id = %s, cl_ord_id = %s" % (order.ord_id, order.cl_ord_id))

    def __req_open_orders(self):
        self.__tws.reqOpenOrders()

    ### EWrapper

    def nextValidId(self, orderId):
        """
        OrderId orderId
        """
        if not self.__next_order_id or orderId > self.__next_order_id:
            self.__next_order_id = orderId

    def tickPrice(self, tickerId, field, price, canAutoExecute):
        """
        TickerId tickerId, TickType field, double price, int canAutoExecute
        """
        record = self.__data_sub_reg.get_data_record(tickerId)
        if record:
            prev = price
            if field == swigibpy.BID:
                prev = record.bid
                record.bid = price
            elif field == swigibpy.ASK:
                prev = record.ask
                record.ask = price
            elif field == swigibpy.LAST:
                prev = record.last
                record.last = price
            elif field == swigibpy.HIGH:
                prev = record.high
                record.high = price
            elif field == swigibpy.LOW:
                prev = record.low
                record.low = price
            elif field == swigibpy.CLOSE:
                prev = record.close
                record.close = price

            if prev != price:
                self.__emit_market_data(field, record)

    def tickSize(self, tickerId, field, size):
        record = self.__data_sub_reg.get_data_record(tickerId)

        if record:
            prev = size

            if field == swigibpy.BID_SIZE:
                prev = record.bid_size
                record.bid_size = size
            elif field == swigibpy.ASK_SIZE:
                prev = record.ask_size
                record.ask_size = size
            elif field == swigibpy.LAST_SIZE:
                prev = record.last_size
                record.last_size = size
            elif field == swigibpy.VOLUME:
                prev = record.vol
                record.vol = size

            if prev != size:
                self.__emit_market_data(field, record)

    def __emit_market_data(self, field, record):
        if record.quote_req and (
                                field == swigibpy.BID or field == swigibpy.BID_SIZE or field == swigibpy.ASK or field == swigibpy.ASK_SIZE) and record.bid > 0 and record.ask > 0:
            self.__data_event_bus.on_next(Quote(instrument=record.inst_id, timestamp=datetime.datetime.now(),
                                                bid=record.bid,
                                                bid_size=record.bid_size,
                                                ask=record.ask,
                                                ask_size=record.ask_size))

        if record.trade_req and (field == swigibpy.LAST or field == swigibpy.LAST_SIZE) and record.last > 0:
            self.__data_event_bus.on_next(
                Trade(instrument=record.inst_id, timestamp=datetime.datetime.now(), price=record.last,
                      size=record.last_size))

    def updateMktDepth(self, id, position, operation, side, price, size):
        """
        TickerId id, int position, int operation, int side, double price, int size
        """
        # TODO fix provider_id
        sub_key = self.__data_sub_reg.get_subscription_key(id)
        self.__data_event_bus.on_next(
            MarketDepth(instrument=sub_key.inst_id, timestamp=datetime.datetime.now(), provider_id=self.ID,
                        position=position,
                        operation=self.__model_factory.convert_ib_md_operation(operation),
                        side=self.__model_factory.convert_ib_md_side(side),
                        price=price, size=size))

    def updateMktDepthL2(self, id, position, marketMaker, operation, side, price, size):
        """
        TickerId id, int position, IBString marketMaker, int operation, int side, double price,
        int size
        """
        # TODO fix provider_id
        sub_key = self.__data_sub_reg.get_subscription_key(id)
        self.__data_event_bus.on_next(
            MarketDepth(instrument=sub_key.inst_id, timestamp=datetime.datetime.now(), provider_id=self.ID,
                        position=position,
                        operation=self.__model_factory.convert_ib_md_operation(operation),
                        side=self.__model_factory.convert_ib_md_side(side),
                        price=price, size=size))

    def historicalData(self, reqId, date, open, high,
                       low, close, volume,
                       barCount, WAP, hasGaps):
        """
        TickerId reqId, IBString const & date, double open, double high, double low, double close,
        int volume, int barCount, double WAP, int hasGaps)
        """
        if barCount < 0:
            return

        sub_key = self.__data_sub_reg.get_subscription_key(reqId)
        record = self.__data_sub_reg.get_data_record(reqId)

        if record:
            record.open = open
            record.high = high
            record.low = low
            record.close = close
            record.vol = volume
            timestamp = self.__model_factory.convert_ib_date(date)
            self.__data_event_bus.on_next(
                Bar(instrument=record.inst_id, timestamp=timestamp, open=open, high=high, low=low,
                    close=close, vol=volume, size=sub_key.bar_size))

    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        """
        TickerId reqId, long time, double open, double high, double low, double close, long volume,
        double wap, int count
        """

        sub_key = self.__data_sub_reg.get_subscription_key(reqId)
        record = self.__data_sub_reg.get_data_record(reqId)

        if record:
            record.open = open
            record.high = high
            record.low = low
            record.close = close
            record.vol = volume

            timestamp = datetime.datetime.fromtimestamp(time)
            self.__data_event_bus.on_next(
                Bar(instrument=record.inst_id, timestamp=timestamp, open=open, high=high, low=low, close=close,
                    vol=volume, size=sub_key.bar_size))

    def orderStatus(self, id, status, filled, remaining, avgFillPrice, permId,
                    parentId, lastFilledPrice, clientId, whyHeld):
        """
        OrderId orderId, IBString const & status, int filled, int remaining, double avgFillPrice,
        int permId, int parentId, double lastFillPrice, int clientId, IBString const & whyHeld
        """
        order = self.__ord_reg.get_order(id)
        if order:
            ord_status = self.__model_factory.convert_ib_ord_status(status)
            create_er = False

            if ord_status == OrdStatus.NEW or ord_status == OrdStatus.PENDING_CANCEL or ord_status == OrdStatus.CANCELLED or (
                            ord_status == OrdStatus.REJECTED and order.status != OrdStatus.REJECTED):
                create_er = True

            if create_er:
                self.__execution_event_bus.on_next(OrderStatusUpdate(
                    broker_id=self.ID,
                    ord_id=order.ord_id,
                    cl_ord_id=order.cl_ord_id,
                    timestamp=datetime.datetime.now(),
                    instrument=order.instrument,
                    filled_qty=filled,
                    avg_price=avgFillPrice,
                    status=ord_status
                ))

    def execDetails(self, reqId, contract, execution):
        """
        int reqId, Contract contract, Execution execution
        """
        order = self.__ord_reg.get_order(execution.orderId)
        if order:
            self.__execution_event_bus.on_next(ExecutionReport(
                broker_id=self.ID,
                ord_id=execution.orderId,
                cl_ord_id=order.cl_ord_id,
                er_id=execution.execId,
                timestamp=self.__model_factory.convert_ib_datetime(execution.time),
                instrument=order.instrument,
                last_qty=execution.shares,
                last_price=execution.price,
                filled_qty=execution.cumQty,
                avg_price=execution.avgPrice
            ))

    def updateAccountValue(self, key, val, currency, accountName):
        """
        IBString const & key, IBString const & val, IBString const & currency, IBString const & accountName
        """
        # TODO
        super(IBBroker, self).updateAccountValue(key, val, currency, accountName)

    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL,
                        accountName):
        """
        Contract contract, int position, double marketPrice, double marketValue, double averageCost,
        double unrealizedPNL, double realizedPNL, IBString const & accountName
        """
        # TODO
        super(IBBroker, self).updatePortfolio(contract, position, marketPrice, marketValue, averageCost, unrealizedPNL,
                                              realizedPNL,
                                              accountName)

    def updateAccountTime(self, timeStamp):
        """
        IBString const & timeStamp
        """
        # TODO
        super(IBBroker, self).updateAccountTime(timeStamp)


    def managedAccounts(self, accountsList):
        """
        IBString const & accountsList
        """
        # TODO

        self.__account = accountsList.split(",")[0]
        self.__req_acct_update()

    def connectionClosed(self):
        # TODO
        super(IBBroker, self).connectionClosed()

    def openOrder(self, orderID, contract, order, orderState):
        """
        OrderId orderId, Contract arg0, Order arg1, OrderState arg2
        """
        # TODO
        super(IBBroker, self).openOrder(orderID, contract, order, orderState)

    def commissionReport(self, commissionReport):
        """
        CommissionReport commissionReport
        """
        # TODO
        super(IBBroker, self).commissionReport(commissionReport)
