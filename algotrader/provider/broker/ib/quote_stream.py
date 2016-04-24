'''
Created on 4/12/16
@author = 'jason'
'''

import logging

import rx
from rx import Observable, Observer
from rx.subjects import Subject
from rx.subjects import BehaviorSubject
from rx.observable import Observable

from algotrader.event.market_data import Quote
from algotrader.utils.clock import RealTimeClock, default_clock
from algotrader.event.event_bus import EventBus
from algotrader.utils.ser_deser import Serializable


class QuoteTick(Serializable):
    def __init__(self, quote, size):
        self.quote = quote
        self.size = size

    def on(self, handler):
        handler.on_quotetick(self)


class QuoteStream(object):
    def __init__(self, instrument, subject=None):
        if not subject:
            subject = EventBus.data_subject
        self.subject = subject
        self.instrument = instrument

        # TODO: is BehaviorSubject a suitable candidate for Observables?
        self.bid = BehaviorSubject(0)
        self.ask = BehaviorSubject(0)
        self.bidSize = BehaviorSubject(0)
        self.askSize = BehaviorSubject(0)

        self.bidBook = rx.Observable \
            .combine_latest( self.bid, self.bidSize, lambda x, y : QuoteTick(x,y))

        self.askBook = rx.Observable \
            .combine_latest( self.ask, self.askSize, lambda x, y : QuoteTick(x,y))

        self.levelone = rx.Observable \
            .combine_latest( self.bidBook, self.askBook, \
                             lambda x, y : Quote(self.instrument, default_clock.current_date_time(), x.quote, x.size, y.quote, y.size )) \
            .subscribe(self.publish)


    def noaction(self,obj):
        pass

    def publish(self, levelone):
        print levelone
        self.subject.on_next(levelone)

    def on_bid(self, bid):
        self.bid.on_next(bid)

    def on_ask(self, ask):
        self.ask.on_next(ask)

    def on_bidsize(self, bidsize):
        self.bidSize.on_next(bidsize)

    def on_asksize(self, asksize):
        self.askSize.on_next(asksize)

