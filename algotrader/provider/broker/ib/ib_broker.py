import threading
from collections import defaultdict

import gevent
import swigibpy

from algotrader.config.broker import IBConfig
from algotrader.event.market_data import Bar, Quote, Trade, MarketDepth
from algotrader.event.market_data import MarketDataType
from algotrader.event.order import OrderStatusUpdate, ExecutionReport, OrdStatus
from algotrader.provider.broker import Broker
from algotrader.provider.broker.ib.ib_model_factory import IBModelFactory
from algotrader.provider.broker.ib.ib_socket import IBSocket
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import HistDataSubscriptionKey, BarSubscriptionType, QuoteSubscriptionType, \
    TradeSubscriptionType, MarketDepthSubscriptionType
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
        self.data_records[req_id] = DataRecord(sub_key.inst_id,
                                               quote_req=sub_key.subscription_type.get_type() == MarketDataType.Quote,
                                               trade_req=sub_key.subscription_type.get_type() == MarketDataType.Trade)

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


class OrderReqRegistry(object):
    def __init__(self):
        self.__clordid_ordreq_dict = defaultdict(dict)
        self.__ordid_ordreq_dict = {}
        self.__clordid_ordid_dict = defaultdict(dict)

    def add_ord_req(self, ord_id, new_ord_req):
        self.__clordid_ordreq_dict[new_ord_req.cl_id][new_ord_req.cl_ord_id] = new_ord_req
        self.__ordid_ordreq_dict[ord_id] = new_ord_req
        self.__clordid_ordid_dict[new_ord_req.cl_id][new_ord_req.cl_ord_id] = ord_id

    def remove_ord_req(self, ord_id, new_ord_req):
        if new_ord_req.cl_id in self.__clordid_ordreq_dict:
            cl_ord_map = self.__clordid_ordreq_dict[new_ord_req.cl_id]
            if new_ord_req.cl_ord_id in cl_ord_map:
                del cl_ord_map[new_ord_req.cl_ord_id]
        if ord_id in self.__ordid_ordreq_dict:
            del self.__ordid_ordreq_dict[ord_id]

    def get_ord_req(self, ord_id=None, cl_id=None, cl_ord_id=None):
        if ord_id:
            return self.__ordid_ordreq_dict.get(ord_id, None)

        if cl_id and cl_ord_id:
            if cl_id in self.__clordid_ordreq_dict:
                return self.__clordid_ordreq_dict.get(cl_id).get(cl_ord_id, None)
            return None

    def get_ord_id(self, cl_id, cl_ord_id):
        if cl_id in self.__clordid_ordid_dict:
            if cl_ord_id in self.__clordid_ordid_dict[cl_id]:
                return self.__clordid_ordid_dict[cl_id][cl_ord_id]
        return None


class IBBroker(IBSocket, Broker, Feed):
    def __init__(self):
        super(IBBroker, self).__init__()

        self.data_sub_reg = SubscriptionRegistry()
        self.ord_req_reg = OrderReqRegistry()

        self.completed_reqs = []
        self.req_callback = {}

    def _start(self, app_context, **kwargs):
        self.ib_config = app_context.app_config.get_config(IBConfig)

        self.next_request_id = self.ib_config.next_request_id
        self.next_order_id = self.ib_config.next_order_id
        self.tws = swigibpy.EPosixClientSocket(self)
        self.port = self.ib_config.port
        self.client_id = self.ib_config.client_id
        self.account = self.ib_config.account

        self.ref_data_mgr = self.app_context.ref_data_mgr
        self.data_event_bus = self.app_context.event_bus.data_subject
        self.execution_event_bus = self.app_context.event_bus.execution_subject
        self.model_factory = IBModelFactory(self.app_context.ref_data_mgr)

        if not self.tws.eConnect("", self.port, self.client_id, poll_auto=False):
            raise RuntimeError('Failed to connect TWS')

        if self.ib_config.use_gevent:
            gevent.spawn(self.poll)
        else:
            thread = threading.Thread(target=self.poll)
            thread.daemon = self.ib_config.daemon
            thread.start()

        if self.account:
            self.__req_acct_update()
        else:
            self.tws.reqManagedAccts()

        self.tws.reqAllOpenOrders()
        self.tws.reqOpenOrders()

        # wait until we get the next_order_id
        # while (not self.next_order_id):
        #    time.sleep(1)

    def poll(self):
        ok = True
        while ok:
            ok = self.tws.checkMessages()

            if ok and (not self.tws or not self.tws.isConnected()):
                ok = False
            gevent.sleep(0)

    def _stop(self):
        self.tws.eDisconnect()
        # todo
        # unsubscribe market data
        # cancel order !?

    def __del__(self):
        self.stop()

    def id(self):
        return Broker.IB

    def get_next_request_id(self):
        req_id = self.next_request_id
        self.next_request_id += 1
        return req_id

    def get_next_order_id(self):
        """get from next_order_id, increment and set the value back to next_order_id, """
        order_id = self.next_order_id
        self.next_order_id += 1
        return order_id

    def next_ord_status_id(self):
        self.app_context.seq_mgr.get_next_sequence("%s.ordstatus" % self.id())

    def subscribe_mktdata(self, *sub_keys):
        for sub_key in sub_keys:
            if isinstance(sub_key, HistDataSubscriptionKey):
                req_func = self.__req_hist_data
            elif isinstance(sub_key.subscription_type, MarketDepthSubscriptionType):
                req_func = self.__req_market_depth
            elif isinstance(sub_key.subscription_type, BarSubscriptionType):
                req_func = self.__req_real_time_bar
            elif isinstance(sub_key.subscription_type, (QuoteSubscriptionType, TradeSubscriptionType)):
                req_func = self.__req_mktdata

            if req_func and not self.data_sub_reg.has_subscription(sub_key=sub_key):
                req_id = self.get_next_request_id()
                self.data_sub_reg.add_subscription(req_id, sub_key)
                contract = self.model_factory.create_ib_contract(sub_key.inst_id)

                req_func(req_id, sub_key, contract)

    def unsubscribe_mktdata(self, *sub_keys):
        for sub_key in sub_keys:
            if isinstance(sub_key, HistDataSubscriptionKey):
                cancel_func = self.__cancel_hist_data
            elif isinstance(sub_key.subscription_type, MarketDepthSubscriptionType):
                req_func = self.__cancel_market_depth
            elif isinstance(sub_key.subscription_type, BarSubscriptionType):
                cancel_func = self.__cancel_real_time_bar
            elif isinstance(sub_key.subscription_type, (QuoteSubscriptionType, TradeSubscriptionType)):
                cancel_func = self.__cancel_mktdata

            if cancel_func:
                req_id = self.data_sub_reg.get_subsciption_id(sub_key)
                if req_id and self.data_sub_reg.remove_subscription(req_id):
                    cancel_func(req_id)

    def __req_mktdata(self, req_id, sub_key, contract):
        self.tws.reqMktData(req_id, contract,
                            '',  # genericTicks
                            False  # snapshot
                            )

    def __cancel_mktdata(self, req_id):
        self.tws.cancelMktData(req_id)

    def __req_real_time_bar(self, req_id, sub_key, contract):
        self.tws.reqRealTimeBars(req_id, contract,
                                 sub_key.subscription_type.bar_size,  # barSizeSetting,
                                 self.model_factory.convert_hist_data_type(sub_key.subscription_type.get_type()),
                                 0  # RTH Regular trading hour
                                 )

    def __cancel_real_time_bar(self, req_id):
        self.tws.cancelRealTimeBars(req_id)

    def __req_market_depth(self, req_id, sub_key, contract):
        self.tws.reqMktDepth(req_id, contract, sub_key.num_rows)

    def __cancel_market_depth(self, req_id):
        self.tws.cancelMktDepth(req_id)

    def __req_hist_data(self, req_id, sub_key, contract):
        self.tws.reqHistoricalData(req_id, contract,
                                   self.model_factory.convert_datetime(sub_key.to_date),  # endDateTime,
                                   self.model_factory.convert_time_period(sub_key.from_date, sub_key.to_date),
                                   # durationStr,
                                   self.model_factory.convert_bar_size(sub_key.subscription_type.bar_size),
                                   # barSizeSetting,
                                   self.model_factory.convert_hist_data_type(sub_key.subscription_type.data_type),
                                   # whatToShow,
                                   0,  # useRTH,
                                   1  # formatDate
                                   )

    def __cancel_hist_data(self, req_id):
        self.tws.cancelHistoricalData(req_id)

    def __request_fa(self):
        self.tws.requestFA(1)  # groups
        self.tws.requestFA(2)  # profile
        self.tws.requestFA(3)  # account_aliases

    def __req_acct_update(self):
        self.tws.reqAccountUpdates(True, self.account)

    def on_new_ord_req(self, new_ord_req):
        logger.debug("[%s] %s" % (self.__class__.__name__, new_ord_req))

        ord_id = self.get_next_order_id()
        self.ord_req_reg.add_ord_req(ord_id, new_ord_req)

        ib_order = self.model_factory.create_ib_order(new_ord_req)
        contract = self.model_factory.create_ib_contract(new_ord_req.inst_id)

        self.tws.placeOrder(ord_id, contract, ib_order)

    def on_ord_replace_req(self, ord_replace_req):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_replace_req))

        existing_ord_req = self.ord_req_reg.get_ord_req(cl_id=ord_replace_req.cl_id,
                                                        cl_ord_id=ord_replace_req.cl_ord_id)
        if existing_ord_req:

            ord_id = self.ord_req_reg.get_ord_id(cl_id=ord_replace_req.cl_id, cl_ord_id=ord_replace_req.cl_ord_id)

            updated_ord_req = existing_ord_req.update_ord_request(ord_replace_req)

            self.ord_req_reg.add_ord_req(ord_id, updated_ord_req)

            ib_order = self.model_factory.create_ib_order(updated_ord_req)
            contract = self.model_factory.create_ib_contract(updated_ord_req.inst_id)
            self.tws.placeOrder(ord_id, contract, ib_order)
        else:
            logger.error("cannot find old order, cl_ord_id = %s" % ord_replace_req.cl_ord_id)

    def on_ord_cancel_req(self, ord_cancel_req):
        logger.debug("[%s] %s" % (self.__class__.__name__, ord_cancel_req))

        ord_id = self.ord_req_reg.get_ord_id(cl_id=ord_cancel_req.cl_id, cl_ord_id=ord_cancel_req.cl_ord_id)

        if ord_id:
            self.tws.cancelOrder(ord_id)
        else:
            logger.error(
                "cannot find old order, cl_id = %s, cl_ord_id = %s" % (ord_cancel_req.cl_id, ord_cancel_req.cl_ord_id))

    def __req_open_orders(self):
        self.tws.reqOpenOrders()

    ### EWrapper

    def nextValidId(self, orderId):
        """
        OrderId orderId
        """
        logger.info("next valid id %s" % orderId)
        if not self.next_order_id or orderId > self.next_order_id:
            self.next_order_id = orderId

    def tickPrice(self, tickerId, field, price, canAutoExecute):
        """
        TickerId tickerId, TickType field, double price, int canAutoExecute
        """
        record = self.data_sub_reg.get_data_record(tickerId)
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
        record = self.data_sub_reg.get_data_record(tickerId)

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
            self.data_event_bus.on_next(Quote(inst_id=record.inst_id, timestamp=self.app_context.clock.now(),
                                              bid=record.bid,
                                              bid_size=record.bid_size,
                                              ask=record.ask,
                                              ask_size=record.ask_size))

        if record.trade_req and (field == swigibpy.LAST or field == swigibpy.LAST_SIZE) and record.last > 0:
            self.data_event_bus.on_next(
                Trade(inst_id=record.inst_id, timestamp=self.app_context.clock.now(), price=record.last,
                      size=record.last_size))

    def updateMktDepth(self, id, position, operation, side, price, size):
        """
        TickerId id, int position, int operation, int side, double price, int size
        """
        # TODO fix provider_id
        sub_key = self.data_sub_reg.get_subscription_key(id)
        self.data_event_bus.on_next(
            MarketDepth(inst_id=sub_key.inst_id, timestamp=self.app_context.clock.now(), provider_id=self.ID,
                        position=position,
                        operation=self.model_factory.convert_ib_md_operation(operation),
                        side=self.model_factory.convert_ib_md_side(side),
                        price=price, size=size))

    def updateMktDepthL2(self, id, position, marketMaker, operation, side, price, size):
        """
        TickerId id, int position, IBString marketMaker, int operation, int side, double price,
        int size
        """
        # TODO fix provider_id
        sub_key = self.data_sub_reg.get_subscription_key(id)
        self.data_event_bus.on_next(
            MarketDepth(inst_id=sub_key.inst_id, timestamp=self.app_context.clock.now(), provider_id=self.ID,
                        position=position,
                        operation=self.model_factory.convert_ib_md_operation(operation),
                        side=self.model_factory.convert_ib_md_side(side),
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

        sub_key = self.data_sub_reg.get_subscription_key(reqId)
        record = self.data_sub_reg.get_data_record(reqId)

        if record:
            record.open = open
            record.high = high
            record.low = low
            record.close = close
            record.vol = volume
            timestamp = self.model_factory.convert_ib_date(date)
            self.data_event_bus.on_next(
                Bar(inst_id=record.inst_id, timestamp=timestamp, open=open, high=high, low=low,
                    close=close, vol=volume, size=sub_key.bar_size))

    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        """
        TickerId reqId, long time, double open, double high, double low, double close, long volume,
        double wap, int count
        """

        sub_key = self.data_sub_reg.get_subscription_key(reqId)
        record = self.data_sub_reg.get_data_record(reqId)

        if record:
            record.open = open
            record.high = high
            record.low = low
            record.close = close
            record.vol = volume

            timestamp = self.model_factory.convert_ib_time(time)
            self.data_event_bus.on_next(
                Bar(inst_id=record.inst_id, timestamp=timestamp, open=open, high=high, low=low, close=close,
                    vol=volume, size=sub_key.subscription_type.bar_size))

    def orderStatus(self, id, status, filled, remaining, avgFillPrice, permId,
                    parentId, lastFilledPrice, clientId, whyHeld):
        """
        OrderId orderId, IBString const & status, int filled, int remaining, double avgFillPrice,
        int permId, int parentId, double lastFillPrice, int clientId, IBString const & whyHeld
        """
        new_ord_req = self.ord_req_reg.get_ord_req(ord_id=id)
        if new_ord_req:
            ord_status = self.model_factory.convert_ib_ord_status(status)
            create_er = False

            if ord_status == OrdStatus.NEW or ord_status == OrdStatus.PENDING_CANCEL or ord_status == OrdStatus.CANCELLED or ord_status == OrdStatus.REJECTED:
                create_er = True

            if create_er:
                self.execution_event_bus.on_next(OrderStatusUpdate(
                    ord_status_id=self.next_ord_status_id(),
                    broker_id=self.ID,
                    ord_id=id,
                    cl_id=new_ord_req.cl_id,
                    cl_ord_id=new_ord_req.cl_ord_id,
                    timestamp=self.app_context.clock.now(),
                    inst_id=new_ord_req.inst_id,
                    filled_qty=filled,
                    avg_price=avgFillPrice,
                    status=ord_status
                ))

    def execDetails(self, reqId, contract, execution):
        """
        int reqId, Contract contract, Execution execution
        """
        new_ord_req = self.ord_req_reg.get_ord_req(ord_id=execution.orderId)
        if new_ord_req:
            self.execution_event_bus.on_next(ExecutionReport(
                broker_id=self.ID,
                ord_id=execution.orderId,
                cl_id=new_ord_req.cl_id,
                cl_ord_id=new_ord_req.cl_ord_id,
                er_id=execution.execId,
                timestamp=self.model_factory.convert_ib_datetime(execution.time),
                inst_id=new_ord_req.inst_id,
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

        self.account = accountsList.split(",")[0]
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

    def reqScannerSubscription(self, num_row=None, inst_type=None, location_code=None, scan_code=None,
                               above_price=None, below_price=None, above_vol=None, avg_opt_vol_above=None,
                               mkt_cap_above=None, mkt_cap_below=None, moody_rating_above=None, moody_rating_below=None,
                               sp_rating_above=None, sp_rating_below=None, mat_date_above=None, mat_date_below=None,
                               coupon_rate_above=None, coupon_rate_below=None, exc_convertible=None,
                               scanner_setting_pairs=None,
                               stk_type_filter=None, callback=None):

        subscription = self.model_factory.create_ib_scanner_subsciption(num_row=num_row, inst_type=inst_type,
                                                                        location_code=location_code,
                                                                        scan_code=scan_code,
                                                                        above_price=above_price,
                                                                        below_price=below_price, above_vol=above_vol,
                                                                        avg_opt_vol_above=avg_opt_vol_above,
                                                                        mkt_cap_above=mkt_cap_above,
                                                                        mkt_cap_below=mkt_cap_below,
                                                                        moody_rating_above=moody_rating_above,
                                                                        moody_rating_below=moody_rating_below,
                                                                        sp_rating_above=sp_rating_above,
                                                                        sp_rating_below=sp_rating_below,
                                                                        mat_date_above=mat_date_above,
                                                                        mat_date_below=mat_date_below,
                                                                        coupon_rate_above=coupon_rate_above,
                                                                        coupon_rate_below=coupon_rate_below,
                                                                        exc_convertible=exc_convertible,
                                                                        scanner_setting_pairs=scanner_setting_pairs,
                                                                        stk_type_filter=stk_type_filter)

        req_id = self.get_next_request_id()
        self._reg_callback(req_id, callback)

        self.tws.reqScannerSubscription(req_id, subscription)

        return req_id

    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        logger.info(
            "scannerData, reqId=%s, rank=%s, contractDetails=%s, distance=%s, benchmark=%s, projection=%s, legsStr=%s",
            reqId, rank, contractDetails, distance, benchmark, projection, legsStr)

    def scannerDataEnd(self, reqId):
        logger.info("scannerDataEnd, reqId=%s", reqId)
        self._complete_req(reqId)

    def reqContractDetails(self, symbol=None, exchange=None, sec_type=None, currency=None, callback=None):
        contract = self.model_factory.create_ib_contract(symbol=symbol, exchange=exchange, sec_type=sec_type,
                                                         currency=currency)
        req_id = self.get_next_request_id()
        self._reg_callback(req_id, callback)

        self.tws.reqContractDetails(req_id, contract)

        return req_id

    def contractDetails(self, reqId, contractDetails):
        """
        int reqId, ContractDetails contractDetails
        """
        cd = contractDetails
        sd = contractDetails.summary
        logger.debug("contractDetails, reqId=%s, conId=%s, symbol=%s, secType=%s, exchange=%s, " +
                     "primaryExchange=%s, expiry=%s, strike=%s, right=%s, " +
                     "multiplier=%s, currency=%s, localSymbol=%s, secIdType=%s, " +
                     "secId=%s, includeExpired=%s, comboLegsDescrip=%s, comboLegs=%s, " +
                     "underComp=%s, " +
                     "marketName=%s, tradingClass=%s, minTick=%s, orderTypes=%s, " +
                     "validExchanges=%s, priceMagnifier=%s, underConId=%s, longName=%s, " +
                     "longName=%s, contractMonth=%s, industry=%s, category=%s, " +
                     "timeZoneId=%s, tradingHours=%s, liquidHours=%s, evRule=%s, " +
                     "evMultiplier=%s, secIdList=%s, cusip=%s, ratings=%s, " +
                     "descAppend=%s, bondType=%s, couponType=%s, callable=%s, " +
                     "putable=%s, coupon=%s, convertible=%s, issueDate=%s, " +
                     "nextOptionDate=%s, nextOptionType=%s, nextOptionPartial=%s, notes=%s"
                     , reqId,
                     sd.conId, sd.symbol, sd.secType, sd.exchange,
                     sd.primaryExchange, sd.expiry, sd.strike, sd.right,
                     sd.multiplier, sd.currency, sd.localSymbol, sd.secIdType,
                     sd.secId, sd.includeExpired, sd.comboLegsDescrip, sd.comboLegs,
                     sd.underComp,
                     cd.marketName, cd.tradingClass, cd.minTick, cd.orderTypes,
                     cd.validExchanges, cd.priceMagnifier, cd.underConId, cd.longName,
                     cd.longName, cd.contractMonth, cd.industry, cd.category,
                     cd.timeZoneId, cd.tradingHours, cd.liquidHours, cd.evRule,
                     cd.evMultiplier, cd.secIdList, cd.cusip, cd.ratings,
                     cd.descAppend, cd.bondType, cd.couponType, cd.callable,
                     cd.putable, cd.coupon, cd.convertible, cd.issueDate,
                     cd.nextOptionDate, cd.nextOptionType, cd.nextOptionPartial, cd.notes)

        self.ref_data_mgr.create_inst(name=cd.longName, type=sd.secType, symbol=sd.symbol, exch_id=sd.exchange,
                                      ccy_id=sd.currency,
                                      # alt_symbols = {Broker.IB: sd.symbol},
                                      # alt_exch_id = {Broker.IB: sd.exchange},
                                      sector=cd.industry, industry=cd.category)

        logger.info("saved")

    def contractDetailsEnd(self, reqId):
        logger.info("contractDetailsEnd, reqId=%s" % reqId)
        self._complete_req(reqId)

    def error(self, id, errorCode, errorString):
        logger.error("error, id=%s, errorCode=%s, errorString=%s", id, errorCode, errorString)
        self._complete_req(id)


    def is_completed(self, req_id):
        return req_id in self.completed_reqs

    def _reg_callback(self, req_id, callback=None):
        if callback:
            self.req_callback[req_id] = callback

    def _complete_req(self, req_id):

        self.completed_reqs.append(req_id)

        if req_id in self.req_callback:
            self.req_callback[req_id].set(req_id)
