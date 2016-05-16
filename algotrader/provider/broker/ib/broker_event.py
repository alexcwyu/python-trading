'''
Created on 4/6/16
@author = 'jason'
'''

from algotrader.event import *
from swigibpy import Contract



class BrokerEvent(Event):
    pass



class ExecutionEvent(Event):
    __slots__ = (
        'broker_id',
        'ord_id',
        'instrument',
        'timestamp'
    )

    def __init__(self, broker_id=None, ord_id=None, instrument=None, timestamp=None):
        # super(ExecutionEvent, self).__init__(instrument, timestamp)
        self.broker_id = broker_id
        self.ord_id = ord_id
        self.instrument = instrument
        self.timestamp = timestamp


class PortfolioMsg(Event):
    __slots__ = (
        'contract',
        'position' ,
        'marketPrice',
        'marketValue' ,
        'averageCost' ,
        'unrealizedPNL' ,
        'realizedPNL' ,
        'accountName'
    )

    def __init__(self, contract,  position,  marketPrice,  marketValue,  averageCost,  unrealizedPNL,  realizedPNL,  accountName);
        self.contract = contract
        self.position =   position
        self.marketPrice =   marketPrice
        self.marketValue =   marketValue
        self.averageCost =   averageCost
        self.unrealizedPNL =   unrealizedPNL
        self.realizedPNL =   realizedPNL
        self.accountName); =   accountName);
