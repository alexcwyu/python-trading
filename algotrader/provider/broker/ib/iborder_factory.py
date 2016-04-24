'''
Created on 4/16/16
@author = 'jason'
'''

from algotrader.event.order import Order, OrdAction, OrdType
from swigibpy import Order as IbOrder

def makeIbOrder(order):

    iborder = IbOrder()
    if (order.action == OrdAction.BUY) :
        iborder.action = 'BUY'
    else :
        iborder.action = 'SELL'

    if order.type == OrdType.LIMIT :
        iborder.lmtPrice = order.limit_price
        iborder.orderType = 'LMT'
    elif order.type == OrdType.MARKET:
        iborder.orderType = 'MKT'
    else :
        iborder.orderType = 'LMT'

    iborder.totalQuantity = order.qty
    iborder.tif = 'DAT'
    iborder.ocaGroup = order.oca_tag
    return iborder


