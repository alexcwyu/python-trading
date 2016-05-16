'''
Created on 4/15/16
@author = 'jason'
'''

import logging

import rx
from rx import Observable, Observer
from rx.subjects import Subject
from rx.subjects import BehaviorSubject
from rx.observable import Observable

from algotrader.event.market_data import Quote, Trade
from algotrader.utils.clock import RealTimeClock, default_clock
from algotrader.event.event_bus import EventBus


class TradeStream(object):
    def __init__(self, instrument, subject=None):
        if not subject:
            subject = EventBus.data_subject
        self.subject = subject
        self.instrument = instrument

        # TODO: is BehaviorSubject a suitable candidate for Observables?
        self.trade = BehaviorSubject(0)
        self.tradeSize = BehaviorSubject(0)

        self.tick = rx.Observable \
            .combine_latest( self.trade, self.tradeSize, \
                             lambda x, y : Trade(self.instrument, default_clock.current_date_time(), x, y )) \
            .subscribe(self.publish)

    def publish(self, tick):
        self.subject.on_next(tick)

    def on_last(self, last):
        self.trade.on_next(last)

    def on_size(self, size):
        self.tradeSize.on_next(size)

