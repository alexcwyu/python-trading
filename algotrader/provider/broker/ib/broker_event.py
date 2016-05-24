'''
Created on 4/6/16
@author = 'jason'
'''

from algotrader.event import *


class BrokerEvent(Event):
    pass


class PortfolioMsg(Event):
    __slots__ = (
        'contract',
        'position',
        'marketPrice',
        'marketValue',
        'averageCost',
        'unrealizedPNL',
        'realizedPNL',
        'accountName'
    )

    def __init__(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL,
                 accountName):
        self.contract = contract
        self.position = position
        self.marketPrice = marketPrice
        self.marketValue = marketValue
        self.averageCost = averageCost
        self.unrealizedPNL = unrealizedPNL
        self.realizedPNL = realizedPNL
        self.accountName = accountName
