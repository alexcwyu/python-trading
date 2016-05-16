'''
Created on 4/16/16
@author = 'jason'
'''

from collections import defaultdict
from pandas.core.common import _ABCGeneric

from algotrader.event.event_bus import EventBus
from algotrader.event.order import MarketDataEventHandler, OrdStatus, OrderStatusUpdate, \
    ExecutionReport
from algotrader.provider.broker.commission import NoCommission
from algotrader.provider.broker.fill_strategy import DefaultFillStrategy
from algotrader.provider.provider import broker_mgr, Broker
from algotrader.provider import Feed
from algotrader.trading import order_mgr
from algotrader.utils import clock
from algotrader.utils import logger
from algotrader.provider.broker.ib.quote_stream import QuoteStream
from algotrader.provider.broker.ib.trade_stream import TradeStream
from algotrader.provider.broker.ib.instrument_mgr import InstrumentManager, IBContractFactory
from algotrader.provider.broker.ib.iborder_factory import makeIbOrder


import sys
from threading import Event
from swigibpy import (EWrapper, EPosixClientSocket, Contract, TagValue,
                      TagValueList, OrderState)
from swigibpy import Order as IbOrder
from Queue import Queue

class IbCallback(EWrapper, MarketDataEventHandler, Feed):
    ID = "IbCallback"

    def __init__(self, instru_mgr, exec_handler=order_mgr, commission=None, fill_strategy=None):
        super(IbCallback, self).__init__()
        self.__next_exec_id = 0
        self.__order_map = defaultdict(dict)
        self.__quote_map = {}
        self.__exec__handler = exec_handler
        # self.__fill_strategy = fill_strategy if fill_strategy is not None else DefaultFillStrategy()
        self.__commission = commission if commission is not None else NoCommission()
        broker_mgr.reg_broker(self)

        self.__order_ids = Queue()
        # some temp dict for Observable
        self.__quotestream_map = {}
        self.__tradestream_map = {}
        self.__instru_mgr = instru_mgr
        self.order_ids = Queue()
        self.init_error()

    def init_error(self):
        setattr(self, "flag_iserror", False)
        setattr(self, "error_msg", "")

    def error(self, id, errorCode, errorString):
        """
        error handling, simple for now

        Here are some typical IB errors
        INFO: 2107, 2106
        WARNING 326 - can't connect as already connected
        CRITICAL: 502, 504 can't connect to TWS.
            200 no security definition found
            162 no trades

        """
        ## Any errors not on this list we just treat as information
        errors_to_trigger =\
            [201, 103, 502, 504, 509, 200, 162, 420, 2105, 1100, 478, 201, 399]

        if errorCode in errors_to_trigger:
            errormsg="IB error id %d errorcode %d string %s" %(id, errorCode, errorString)
            print errormsg
            setattr(self, "flag_iserror", True)
            setattr(self, "error_msg", True)

        ## Wrapper functions don't have to return anything

    def nextValidId(self, validOrderId):
        self.order_ids.put(validOrderId)


    def start(self):
        # EventBus.data_subject.subscribe(self.on_next)
        pass

    def stop(self):
        pass

    def id(self):
        return IbCallback.ID

    # def next_exec_id(self):
    #     if (self.__next_exec_id == 0):
    #         WAIT_TIME = 10
    #         __next_exec_id = self.order_ids.get(timeout=WAIT_TIME)
    #         self.__next_exec_id = __next_exec_id + 1
    #         return __next_exec_id
    #     else :
    #         __next_exec_id = self.__next_exec_id
    #         self.__next_exec_id += 1
    #         return __next_exec_id

    def tickPrice(self, tickerId, field, price, canAutoExecute):
        """
        :param tickerId: TickerId
        :param field: TickType
        :param price: double
        :param canAutoExecute: int
        :return:
        """

        # print "[%s] tickerId %s, field %s, price %s, canAutoExecute %s" % (self.__class__.__name__, tickerId, field, price, canAutoExecute)
        logger.info("[%s] tickerId %s, field %s, price %s, canAutoExecute %s" % (self.__class__.__name__, tickerId, field, price, canAutoExecute))
        qs = None
        ts = None
        if self.__quotestream_map.has_key(tickerId):
            qs = self.__quotestream_map.get(tickerId)
        else:
            qs = QuoteStream("AAPL")

        if self.__tradestream_map.has_key(tickerId):
            ts = self.__tradestream_map.get(tickerId)
        else:
            ts = TradeStream("AAPL")

        if field == "BIDPRICE":
            qs.on_bid(price)
        elif field == "ASKPRICE":
            qs.on_ask(price)
        elif field == "LASTPRICE":
            ts.on_last(price)
        else:
            pass

        self.__quotestream_map[tickerId] = qs
        self.__tradestream_map[tickerId] = ts

    def tickSize(self, tickerId, field, size):
        """
        :param tickerId:
        :param field:
        :param size:
        :return:
        """
        qs = None
        ts = None
        if self.__quotestream_map.has_key(tickerId):
            qs = self.__quotestream_map.get(tickerId)
        else:
            qs = QuoteStream("AAPL")

        if self.__tradestream_map.has_key(tickerId):
            ts = self.__tradestream_map.get(tickerId)
        else:
            ts = TradeStream("AAPL")

        if field == "BIDPRICE":
            qs.on_bid(price)
        elif field == "ASKPRICE":
            qs.on_ask(price)
        elif field == "LASTPRICE":
            ts.on_last(price)

        self.__quotestream_map[tickerId] = qs
        self.__tradestream_map[tickerId] = ts

    def updateAccountValue(self, *args, **kwargs):
        """updateAccountValue(EWrapper self, IBString const & key, IBString const & val, IBString const & currency, IBString const & accountName)"""
        # return _swigibpy.EWrapper_updateAccountValue(self, *args, **kwargs)
        pass

    def updatePortfolio(self, *args, **kwargs):
        """
        updatePortfolio(EWrapper self, Contract contract, int position, double marketPrice, double marketValue, double averageCost,
            double unrealizedPNL, double realizedPNL, IBString const & accountName)
        """
        # return _swigibpy.EWrapper_updatePortfolio(self, *args, **kwargs)
        pass

    def updateMktDepth(self, *args, **kwargs):
        """updateMktDepth(EWrapper self, TickerId id, int position, int operation, int side, double price, int size)"""
        # return _swigibpy.EWrapper_updateMktDepth(self, *args, **kwargs)
        pass

    def updateMktDepthL2(self, *args, **kwargs):
        """
        updateMktDepthL2(EWrapper self, TickerId id, int position, IBString marketMaker, int operation, int side, double price,
            int size)
        """
        # return _swigibpy.EWrapper_updateMktDepthL2(self, *args, **kwargs)
        pass


    def historicalData(self, reqId, date, open, high,
                       low, close, volume,
                       barCount, WAP, hasGaps):
        """
        :param reqId:
        :param date:
        :param open:
        :param high:
        :param low:
        :param close:
        :param volume:
        :param barCount:
        :param WAP:
        :param hasGaps:
        :return:
        """
        if date[:8] == 'finished':
            logger.info("[%s] History request complete for id: %s" % (self.__class__.__name__, reqId))
            # self.got_history.set()
        else:
            print date
            pydate = datetime.strptime(date,  "%Y%m%d  %H:%M:%S")
            logger.debug(("History %s - Open: %s, High: %s, Low: %s, Close: "
                   "%s, Volume: %d") % (pydate, open, high, low, close, volume))




    def orderStatus(self, id, status, filled, remaining, avgFillPrice, permId,
                    parentId, lastFilledPrice, clientId, whyHeld):
        """
        :param id:
        :param status:
        :param filled:
        :param remaining:
        :param avgFillPrice:
        :param permId:
        :param parentId:
        :param lastFilledPrice:
        :param clientId:
        :param whyHeld:
        :return:
        """
        # IB specific

        logger.debug("[%s] %s %s %s %s %s %s %s %s %s" % (self.__class__.__name__,
                                                          status,
                                                          filled,
                                                          remaining,
                                                          avgFillPrice,
                                                          permId,
                                                          parentId,
                                                          lastFilledPrice,
                                                          clientId,
                                                          whyHeld))

        # print(("Order #%s - %s (filled %d, remaining %d, avgFillPrice %f,"
        #        "last fill price %f)") %
        #       (id, status, filled, remaining, avgFillPrice, lastFilledPrice))

        downStreamStatus = none
        if status == "PreSubmitted" :
            downStreamStatus = OrdStatus.REPLACED
        elif status == "Submitted" :
            downStreamStatus = OrdStatus.NEW
        elif status == "FILLED" :
            if remaining > 0 :
                downStreamStatus = OrdStatus.PARTIALLY_FILLED
            else :
                downStreamStatus = OrdStatus.FILLED

        order_update = ExecutionReport(self.ID, id, instrument, timestamp=clock.default_clock.current_date_time(),
                                       filled_qty= filled, filled_price=avgFillPrice, commission=0, status = downStreamStatus  )
        self.__exec__handler.on_ord_upd(ord_update)

    # self, broker_id=None, ord_id=None, instrument=None, timestamp=None, er_id=None, filled_qty=0, filled_price=0, commission=0,
    #                  status=OrdStatus.NEW):


    def openOrderEnd(self):
        '''Not relevant for our example'''
        pass

    def execDetails(self, id, contract, execution):
        '''Not relevant for our example'''
        pass

    def managedAccounts(self, openOrderEnd):
        '''Not relevant for our example'''
        pass

    ###############
    # end of IB method

    def openOrder(self, orderID, contract, order, orderState):
        orderState = OrderState()
        logger.debug("[%s] %s" % (self.__class__.__name__, event))
        # orderState.commission
        # orderState.commissionCurrency
        # orderState.equityWithLoan
        # orderState.initMargin
        # orderState.maintMargin
        # orderState.maxCommission
        # orderState.minCommission
        # orderState.status
        # orderState.thisown
        # orderState.warningText
        logger.info("[%s] Order open for %s" % (self.__class__.__name__, contract.symbol))

    def commissionReport(self, commissionReport):
        print 'Commission %s %s P&L: %s' % (commissionReport.currency,
                                            commissionReport.commission,
                                            commissionReport.realizedPNL)


    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName):
        """EWrapper self, Contract contract, int position, double marketPrice, double marketValue, double averageCost,
            double unrealizedPNL, double realizedPNL, IBString const & accountName """
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

    def on_order(self, order):
        logger.debug("[%s] %s" % (self.__class__.__name__, order))

        self.__add_order(order)
        # self.__send_exec_report(order, 0, 0, OrdStatus.SUBMITTED)

        # self.__tws.placeOrder(self.next_exec_id(), order.instrument)
        # fill_info = self.__fill_strategy.process_new_order(order)
        # executed = self.execute(order, fill_info)

    def __add_order(self, order):
        orders = self.__order_map[order.instrument]
        orders[order.ord_id] = order

    def __remove_order(self, order):
        if order.instrument in self.__order_map:
            orders = self.__order_map[order.instrument]
            if order.ord_id in orders:
                del orders[order.ord_id]

    def execute(self, order, fill_info):
        if not fill_info or fill_info.fill_price <=0 or fill_info.fill_price<=0:
            return False

        filled_price = fill_info.fill_price
        filled_qty = fill_info.fill_qty

        if order.is_done():
            self.__remove_order(order)
            return False

        if filled_qty < order.leave_qty():
            self.__send_exec_report(order, filled_price, filled_qty, OrdStatus.PARTIALLY_FILLED)
            return False
        else:
            filled_qty = order.leave_qty()
            self.__send_exec_report(order, filled_price, filled_qty, OrdStatus.FILLED)
            self.__remove_order(order)
            return True

    def __send_status(self, order, ord_status):
        ord_update = OrderStatusUpdate(broker_id=IbCallback.ID, ord_id=order.ord_id, instrument=order.instrument,
                                       timestamp=clock.default_clock.current_date_time(), status=ord_status)
        self.__exec__handler.on_ord_upd(ord_update)

    def __send_exec_report(self, order, filled_price, filled_qty, ord_status):
        commission = self.__commission.calc(order, filled_price, filled_qty)
        exec_report = ExecutionReport(broker_id=IbCallback.ID, ord_id=order.ord_id, instrument=order.instrument,
                                      timestamp=clock.default_clock.current_date_time(), er_id=self.next_exec_id(),
                                      filled_qty=filled_qty,
                                      filled_price=filled_price, status=ord_status,
                                      commission=commission)

        self.__exec__handler.on_exec_report(exec_report)

    def _get_orders(self):
        return self.__order_map



    def updateMktDepth(self, *args, **kwargs):
        """updateMktDepth(EWrapper self, TickerId id, int position, int operation, int side, double price, int size)"""
        return _swigibpy.EWrapper_updateMktDepth(self, *args, **kwargs)


    def tickGeneric(self, tickerId, tickType, value):
        logger.debug("[%s] : tickerId %s, tickType %s, value %s" % (self.__class__.__name__, tickerId, tickType, value))


    def tickString(self,tickerId, tickType, value):
        logger.debug("[%s] : tickerId %s, tickType %s, value %s" % (self.__class__.__name__, tickerId, tickType, value))
# gateway = IbCallback();
