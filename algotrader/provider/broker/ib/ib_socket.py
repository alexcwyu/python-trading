import swigibpy

from algotrader.utils.logging import logger


class IBSocket(swigibpy.EWrapper):
    def __init__(self):
        super(IBSocket, self).__init__()

    def nextValidId(self, orderId):
        """
        OrderId orderId
        """
        logger.debug("nextValidId, orderId=%s", orderId)

    def contractDetails(self, reqId, contractDetails):
        """
        int reqId, ContractDetails contractDetails
        """
        logger.debug("contractDetails, reqId=%s, contractDetails=%s", reqId, contractDetails)

    def contractDetailsEnd(self, reqId):
        logger.debug("contractDetailsEnd, reqId=%s", reqId)

    def bondContractDetails(self, reqId, contractDetails):
        """
        int reqId, ContractDetails contractDetails
        """
        logger.debug("bondContractDetails, reqId=%s, contractDetails=%s", reqId, contractDetails)

    def error(self, id, errorCode, errorString):
        logger.error("error, id=%s, errorCode=%s, errorString=%s", id, errorCode, errorString)

    def tickPrice(self, tickerId, field, price, canAutoExecute):
        """
        TickerId tickerId, TickType field, double price, int canAutoExecute
        """
        logger.debug("tickPrice, tickerId=%s field=%s price=%s canAutoExecute=%s", tickerId, field, price,
                     canAutoExecute)

    def tickSize(self, tickerId, field, size):
        logger.debug("tickSize, tickerId=%s field=%s size=%s", tickerId, field, size)

    def tickOptionComputation(self, tickerId, tickType, impliedVol, delta, optPrice, gamma, vega, theta, undPrice):
        """
        TickerId tickerId, TickType tickType, double impliedVol, double delta, double optPrice,
        double pvDividend, double gamma, double vega, double theta, double undPrice
        """
        logger.debug(
            "tickOptionComputation, tickerId=%s tickType=%s simpliedVol=%s delta=%s optPrice=%s, gamma=%s, vega=%s, theta=%s, undPrice=%s",
            tickerId, tickType, impliedVol, delta, optPrice, gamma, vega, theta, undPrice)

    def tickGeneric(self, tickerId, tickType, value):
        """
        TickerId tickerId, TickType tickType, double value
        """
        logger.debug("tickGeneric, tickerId=%s tickType=%s value=%s", tickerId, tickType, value)

    def tickString(self, tickerId, tickType, value):
        """
        TickerId tickerId, TickType tickType, IBString const & value
        """
        logger.debug("tickString, tickerId=%s tickType=%s value=%s", tickerId, tickType, value)

    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, totalDividends, holdDays, futureExpiry,
                dividendImpact, dividendsToExpiry):
        """
        EWrapper self, TickerId tickerId, TickType tickType, double basisPoints, IBString const & formattedBasisPoints,
        double totalDividends, int holdDays, IBString const & futureExpiry,
        double dividendImpact, double dividendsToExpiry
        """
        logger.debug(
            "tickEFP, tickerId=%s tickType=%s basisPoints=%s formattedBasisPoints=%s totalDividends=%s, holdDays=%s, futureExpiry=%s, dividendImpact=%s, dividendsToExpiry=%s",
            tickerId, tickType, basisPoints, formattedBasisPoints, totalDividends, holdDays, futureExpiry,
            dividendImpact, dividendsToExpiry)

    def updateAccountValue(self, key, val, currency, accountName):
        """
        IBString const & key, IBString const & val, IBString const & currency, IBString const & accountName
        """
        logger.debug("updateAccountValue, key=%s val=%s currency=%s accountName=%s", key, val, currency,
                     accountName)

    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL,
                        accountName):
        """
        Contract contract, int position, double marketPrice, double marketValue, double averageCost,
        double unrealizedPNL, double realizedPNL, IBString const & accountName
        """
        logger.debug(
            "updatePortfolio, contract=%s position=%s marketPrice=%s marketValue=%s averageCost=%s, unrealizedPNL=%s, realizedPNL=%s, accountName=%s",
            contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL,
            accountName)

    def updateAccountTime(self, timeStamp):
        """
        IBString const & timeStamp
        """
        logger.debug("updateAccountTime, timeStamp=%s", timeStamp)

    def accountDownloadEnd(self, accountName):
        """
        IBString const & accountName
        """
        logger.debug("accountDownloadEnd, accountName=%s", accountName)

    def updateMktDepth(self, id, position, operation, side, price, size):
        """
        TickerId id, int position, int operation, int side, double price, int size
        """
        logger.debug("updateMktDepth, id=%s position=%s operation=%s side=%s price=%s size=%s", id, position, operation,
                     side, price, size)

    def updateMktDepthL2(self, id, position, marketMaker, operation, side, price, size):
        """
        TickerId id, int position, IBString marketMaker, int operation, int side, double price,
        int size
        """
        logger.debug("updateMktDepthL2, id=%s position=%s marketMaker=%s operation=%s side=%s price=%s size=%s", id,
                     position, marketMaker, operation, side, price, size)

    def historicalData(self, reqId, date, open, high,
                       low, close, volume,
                       barCount, WAP, hasGaps):
        """
        TickerId reqId, IBString const & date, double open, double high, double low, double close,
        int volume, int barCount, double WAP, int hasGaps)
        """
        logger.debug(
            "historicalData, reqId=%s date=%s open=%s high=%s low=%s close=%s volume=%s barCount=%s WAP=%s hasGaps=%s",
            reqId, date, open, high,
            low, close, volume,
            barCount, WAP, hasGaps)

    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        """
        TickerId reqId, long time, double open, double high, double low, double close, long volume,
        double wap, int count
        """
        logger.debug("realtimeBar, reqId=%s time=%s open=%s high=%s low=%s close=%s volume=%s wap=%s count=%s", reqId,
                     time, open, high,
                     low, close, volume,
                     wap, count)

    def currentTime(self, time):
        """
        long time
        """
        logger.debug("currentTime, time=%s", time)

    def orderStatus(self, id, status, filled, remaining, avgFillPrice, permId,
                    parentId, lastFilledPrice, clientId, whyHeld):
        """
        OrderId orderId, IBString const & status, int filled, int remaining, double avgFillPrice,
        int permId, int parentId, double lastFillPrice, int clientId, IBString const & whyHeld
        """
        logger.debug(
            "orderStatus, id=%s, status=%s, filled=%s, remaining=%s, avgFillPrice=%s, permId=%s, parentId=%s, lastFilledPrice=%s, clientId=%s, whyHeld=%s",
            id, status, filled, remaining, avgFillPrice, permId,
            parentId, lastFilledPrice, clientId, whyHeld)

    def openOrderEnd(self):
        logger.debug("openOrderEnd")

    def execDetails(self, reqId, contract, execution):
        """
        int reqId, Contract contract, Execution execution
        """
        logger.debug("execDetails, reqId=%s, contract=%s, execution=%s", reqId, contract, execution)

    def execDetailsEnd(self, reqId):
        """
        int reqId
        """
        logger.debug("execDetailsEnd, reqId=%s", reqId)

    def managedAccounts(self, accountsList):
        """
        IBString const & accountsList
        """
        logger.debug("managedAccounts, accountsList=%s", accountsList)

    def connectionClosed(self):
        logger.warn("connectionClosed")

    def openOrder(self, orderID, contract, order, orderState):
        """
        OrderId orderId, Contract arg0, Order arg1, OrderState arg2
        """
        logger.debug("openOrder, orderID=%s, contract=%s, order=%s, orderState=%s", orderID, contract, order,
                     orderState)

    def commissionReport(self, commissionReport):
        """
        CommissionReport commissionReport
        """
        logger.debug("commissionReport, commissionReport=%s", commissionReport)

    def scannerParameters(self, xml):
        """
        IBString const & xml
        """
        logger.debug("scannerParameters, xml=%s", xml)

    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        """
        int reqId, int rank, ContractDetails contractDetails, IBString const & distance,
        IBString const & benchmark, IBString const & projection, IBString const & legsStr
        """
        logger.debug(
            "scannerData, reqId=%s, rank=%s, contractDetails=%s, distance=%s, benchmark=%s, projection=%s, legsStr=%s",
            reqId, rank, contractDetails, distance, benchmark, projection, legsStr)

    def scannerDataEnd(self, reqId):
        """
        int reqId
        """
        logger.debug("scannerDataEnd, reqId=%s", reqId)

    def fundamentalData(self, reqId, data):
        """
        TickerId reqId, IBString const & data
        """
        logger.debug("fundamentalData, reqId=%s, data=%s", reqId, data)

    def deltaNeutralValidation(self, reqId, underComp):
        """
        int reqId, UnderComp underComp
        """
        logger.debug("deltaNeutralValidation, reqId=%s, underComp=%s", reqId, underComp)

    def marketDataType(self, reqId, marketDataType):
        """
        TickerId reqId, int marketDataType
        """
        logger.debug("marketDataType, reqId=%s, marketDataType=%s", reqId, marketDataType)

    def tickSnapshotEnd(self, reqId):
        """
        int reqId
        """
        logger.debug("tickSnapshotEnd, reqId=%s", reqId)

    def updateNewsBulletin(self, msgId, msgType, newsMessage, originExch):
        """
        int msgId, int msgType, IBString const & newsMessage, IBString const & originExch
        """
        logger.debug("updateNewsBulletin, msgId=%s, msgType=%s, newsMessage=%s, originExch=%s", msgId, msgType,
                     newsMessage, originExch)

    def receiveFA(self, pFaDataType, cxml):
        """
        faDataType pFaDataType, IBString const & cxml
        """
        logger.debug("receiveFA, pFaDataType=%s, cxml=%s", pFaDataType, cxml)
