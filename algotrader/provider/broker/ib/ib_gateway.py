'''
Created on 4/5/16
@author = 'jason'
'''

from datetime import datetime
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
from algotrader.provider.broker.ib.ib_callback import IbCallback


import sys
from threading import Event
from swigibpy import (EWrapper, EPosixClientSocket, Contract, TagValue,
                      TagValueList)
from swigibpy import Order as IbOrder

class IbGateway(Broker):
    ID = "IbGateway"

    def __init__(self, instru_mgr=None):
        if not instru_mgr :
            instru_mgr = InstrumentManager()
        self.__callback = IbCallback(instru_mgr=instru_mgr)
        self.__tws = EPosixClientSocket(self.__callback)
        self.__instru_mgr = instru_mgr
        self.__hasRequestedMktData = False
        self.__contractFactory = IBContractFactory(self.__instru_mgr)

    def start(self):
        self.__instru_mgr.start()
        if not self.__tws.eConnect("" , 7496, 42):
            raise RuntimeError('Failed to connect TWS')

    def stop(self):
        self.__instru_mgr.stop()
        if self.__hasRequestedMktData:
            self.cancel_mktdata()
        self.__tws.eDisconnect()

    def __del__(self):
        self.stop()

    def id(self):
        return IbGateway.ID

    def req_mktdata(self):
        logger.debug("[%s] " % (self.__class__.__name__))
        self.__hasRequestedMktData = True
        for id, row in self.__instru_mgr.instrument_repo.iterrows():
            logger.debug("[%s] requesting %s" % (self.__class__.__name__, row['symbol']))
            self.__tws.reqMktData(id, self.__contractFactory.buildStockOrCashContract(row['symbol']), '' , False)

    def cancel_mktdata(self):
        for id, row in self.__instru_mgr.instrument_repo.iterrows():
            self.__tws.cancelMktData(id)

    def on_order(self, order):
        logger.debug("[%s] %s" % (self.__class__.__name__, order))

        iborder = makeIbOrder(order)
        contract = self.__contractFactory.buildStockOrCashContract(symbol=order.instrument)
        self.__callback.on_order(order) # let the callback class has a reference to the order so that once the IB return the exeuction report we can undate the order accordingly
        self.__tws.placeOrder(order.ord_id, contract, iborder) # assume the oorder_mgr is started with IB next order id

    def cancel_order(self, order):
        self.__tws.cancelOrder(order.ord_id)

    def req_open_orders(self):
        self.__tws.reqOpenOrders()

    def req_mkt_depth(self, market_orderbook_numdepth=5):
        for id, row in self.__instru_mgr.instrument_repo.iterrows():
            self.__tws.reqMktDepth(id, self.__contractFactory.buildStockOrCashContract(row['symbol']),
                                   market_orderbook_numdepth)

    def cancel_mkt_depth(self, *args, **kwargs):
        for id, row in self.__instru_mgr.instrument_repo.iterrows():
            self.__tws.cancelMktDepth(id)


    def reqHistoricalData(self, ids, up_to_day= datetime.today()):
        for id, row in self.__instru_mgr.instrument_repo.iterrows():
            contract = self.__contractFactory.buildStockOrCashContract(row['symbol'], row['secType'],
                                                                                 row['exchange'],
                                                                                 row['currency'])
            self.__tws.reqHistoricalData(id,                  # tickerId,
                                         contract,            # contract,
                                         up_to_day.strftime("%Y%m%d %H:%M:%S %Z"),       # endDateTime,
                                         "1 W",                # durationStr,
                                         "1 min",              # barSizeSetting,
                                         "MIDPOINT",           # whatToShow,
                                         0,                    # useRTH,
                                         1)                     # formatDate



#gateway = IbGateway()