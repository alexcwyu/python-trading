import sys
from datetime import datetime
from threading import Event

from swigibpy import EWrapper, EPosixClientSocket, Contract, Order, TagValue, TagValueList

WAIT_TIME = 10.0

try:
    # Python 2 compatibility
    input = raw_input
    from Queue import Queue
except:
    from queue import Queue


###


class SwigIBClient(EWrapper):
    '''Callback object passed to TWS, these functions will be called directly
    by TWS.
    '''

    def __init__(self, port = 4001, client_id=12):
        super(SwigIBClient, self).__init__()

        self.tws = EPosixClientSocket(self)
        self.port = port
        self.client_id = client_id

        self.got_history = Event()
        self.got_contract = Event()
        self.got_err = Event()
        self.order_filled = Event()
        self.order_ids = Queue()

    def execDetails(self, id, contract, execution):
        pass


    def managedAccounts(self, openOrderEnd):
        pass

    ### Order
    def nextValidId(self, validOrderId):
        '''Capture the next order id'''
        self.order_ids.put(validOrderId)

    def orderStatus(self, id, status, filled, remaining, avgFillPrice, permId,
                    parentId, lastFilledPrice, clientId, whyHeld):
        print(("Order #%s - %s (filled %d, remaining %d, avgFillPrice %f,"
               "last fill price %f)") %
              (id, status, filled, remaining, avgFillPrice, lastFilledPrice))
        if remaining <= 0:
            self.order_filled.set()

    def openOrder(self, orderID, contract, order, orderState):
        print("Order opened for %s" % contract.symbol)


    def openOrderEnd(self):
        pass


    def commissionReport(self, commissionReport):
        print 'Commission %s %s P&L: %s' % (commissionReport.currency,
                                            commissionReport.commission,
                                            commissionReport.realizedPNL)


    ### Historical data
    def historicalData(self, reqId, date, open, high,
                       low, close, volume,
                       barCount, WAP, hasGaps):

        if date[:8] == 'finished':
            print("History request complete")
            self.got_history.set()
        else:
            date = datetime.strptime(date, "%Y%m%d").strftime("%d %b %Y")
            print(("History %s - Open: %s, High: %s, Low: %s, Close: "
                   "%s, Volume: %d") % (date, open, high, low, close, volume))


    ### Contract details
    def contractDetailsEnd(self, reqId):
        print("Contract details request complete, (request id %i)" % reqId)

    def contractDetails(self, reqId, contractDetails):
        print("Contract details received (request id %i):" % reqId)
        print("callable: %s" % contractDetails.callable)
        print("category: %s" % contractDetails.category)
        print("contractMonth: %s" % contractDetails.contractMonth)
        print("convertible: %s" % contractDetails.convertible)
        print("coupon: %s" % contractDetails.coupon)
        print("industry: %s" % contractDetails.industry)
        print("liquidHours: %s" % contractDetails.liquidHours)
        print("longName: %s" % contractDetails.longName)
        print("marketName: %s" % contractDetails.marketName)
        print("minTick: %s" % contractDetails.minTick)
        print("nextOptionPartial: %s" % contractDetails.nextOptionPartial)
        print("orderTypes: %s" % contractDetails.orderTypes)
        print("priceMagnifier: %s" % contractDetails.priceMagnifier)
        print("putable: %s" % contractDetails.putable)
        if contractDetails.secIdList is not None:
            for secId in contractDetails.secIdList:
                print("secIdList: %s" % secId)
        else:
            print("secIdList: None")

        print("subcategory: %s" % contractDetails.subcategory)
        print("tradingHours: %s" % contractDetails.tradingHours)
        print("timeZoneId: %s" % contractDetails.timeZoneId)
        print("underConId: %s" % contractDetails.underConId)
        print("evRule: %s" % contractDetails.evRule)
        print("evMultiplier: %s" % contractDetails.evMultiplier)

        contract = contractDetails.summary

        print("\nContract Summary:")
        print("exchange: %s" % contract.exchange)
        print("symbol: %s" % contract.symbol)
        print("secType: %s" % contract.secType)
        print("currency: %s" % contract.currency)
        print("tradingClass: %s" % contract.tradingClass)
        if contract.comboLegs is not None:
            for comboLeg in contract.comboLegs:
                print("comboLegs: %s - %s" %
                      (comboLeg.action, comboLeg.exchange))
        else:
            print("comboLegs: None")

        print("\nBond Values:")
        print("bondType: %s" % contractDetails.bondType)
        print("couponType: %s" % contractDetails.couponType)
        print("cusip: %s" % contractDetails.cusip)
        print("descAppend: %s" % contractDetails.descAppend)
        print("issueDate: %s" % contractDetails.issueDate)
        print("maturity: %s" % contractDetails.maturity)
        print("nextOptionDate: %s" % contractDetails.nextOptionDate)
        print("nextOptionType: %s" % contractDetails.nextOptionType)
        print("notes: %s" % contractDetails.notes)
        print("ratings: %s" % contractDetails.ratings)
        print("validExchanges: %s" % contractDetails.validExchanges)

        self.got_contract.set()


    ### Error
    def error(self, id, errCode, errString):

        if errCode == 165 or (errCode >= 2100 and errCode <= 2110):
            print("TWS warns %s" % errString)
        elif errCode == 502:
            print('Looks like TWS is not running, '
                  'start it up and try again')
            sys.exit()
        elif errCode == 501:
            print("TWS reports error in client: %s" % errString)
        elif errCode >= 1100 and errCode < 2100:
            print("TWS reports system error: %s" % errString)
        elif errCode == 321:
            print("TWS complaining about bad request: %s" % errString)
        else:
            super(SwigIBClient, self).error(id, errCode, errString)
        self.got_err.set()

    def winError(self, msg, lastError):
        print("TWS reports API error: %s" % msg)
        self.got_err.set()

    def pyError(self, type, val, tb):
        sys.print_exception(type, val, tb)



    ###
    def connect(self):
        if not self.tws.eConnect("", self.port, self.client_id):
            raise RuntimeError('Failed to connect to TWS')


    def disconnect(self):
        print("\nDisconnecting...")
        self.tws.eDisconnect()


    def create_contract(self):
        # Simple contract for GOOG
        contract = Contract()
        contract.exchange = "SMART"
        contract.symbol = "GOOG"
        contract.secType = "STK"
        contract.currency = "USD"
        return contract


    def request_contract_details(self, contract):
        today = datetime.today()

        print("Requesting contract details...")

        # Perform the request
        self.tws.reqContractDetails(
            42,                                         # reqId,
            contract,                                   # contract,
        )

        print("\n====================================================================")
        print(" Contract details requested, waiting %ds for TWS responses" % WAIT_TIME)
        print("====================================================================\n")


        try:
            self.callback.got_contract.wait(timeout=WAIT_TIME)
        except KeyboardInterrupt:
            pass
        finally:
            if not self.callback.got_contract.is_set():
                print('Failed to get contract within %d seconds' % WAIT_TIME)



    def request_hist_data(self, contract):
        today = datetime.today()

        print("Requesting historical data for %s" % contract.symbol)

        # Request some historical data.
        self.tws.reqHistoricalData(
            2,                                          # tickerId,
            contract,                                   # contract,
            today.strftime("%Y%m%d %H:%M:%S %Z"),       # endDateTime,
            "1 W",                                      # durationStr,
            "1 day",                                    # barSizeSetting,
            "TRADES",                                   # whatToShow,
            0,                                          # useRTH,
            1                                     # formatDate
        )

        print("\n====================================================================")
        print(" History requested, waiting %ds for TWS responses" % WAIT_TIME)
        print("====================================================================\n")


        try:
            self.callback.got_history.wait(timeout=WAIT_TIME)
        except KeyboardInterrupt:
            pass
        finally:
            if not self.callback.got_history.is_set():
                print('Failed to get history within %d seconds' % WAIT_TIME)



    def subscribe_market_data(self, contract):
        pass

    def unsubscribe_market_data(self, contract):
        pass




    def place_order(self, contract):
        print('Waiting for valid order id')
        order_id = self.callback.order_ids.get(timeout=WAIT_TIME)
        if not order_id:
            raise RuntimeError('Failed to receive order id after %ds' % WAIT_TIME)

        # Order details
        algoParams = TagValueList()
        algoParams.append(TagValue("componentSize", "3"))
        algoParams.append(TagValue("timeBetweenOrders", "60"))
        algoParams.append(TagValue("randomizeTime20", "1"))
        algoParams.append(TagValue("randomizeSize55", "1"))
        algoParams.append(TagValue("giveUp", "1"))
        algoParams.append(TagValue("catchUp", "1"))
        algoParams.append(TagValue("waitForFill", "1"))
        algoParams.append(TagValue("startTime", "20110302-14:30:00 GMT"))
        algoParams.append(TagValue("endTime", "20110302-21:00:00 GMT"))

        order = Order()
        order.action = 'BUY'
        order.lmtPrice = 140
        order.orderType = 'LMT'
        order.totalQuantity = 10
        order.algoStrategy = "AD"
        order.tif = 'DAT'
        order.algoParams = algoParams
        #order.transmit = False


        print("Placing order for %d %s's (id: %d)" % (order.totalQuantity,
                                                      contract.symbol, order_id))

        # Place the order
        self.tws.placeOrder(
            order_id,                                   # orderId,
            contract,                                   # contract,
            order                                       # order
        )

        print("\n====================================================================")
        print(" Order placed, waiting %ds for TWS responses" % WAIT_TIME)
        print("====================================================================\n")


        print("Waiting for order to be filled..")

        try:
            self.callback.order_filled.wait(WAIT_TIME)
        except KeyboardInterrupt:
            pass
        finally:
            if not self.callback.order_filled.is_set():
                print('Failed to fill order')


if __name__ =="__main__":
    pass