import abc
from rx.concurrency import GEventScheduler
from rx.observable import Observable, Observer
from rx.subjects import Subject
import rx
import datetime

from atom.api import Atom, Unicode, Range, Bool, observe, Enum, Str, Value, Float, Long

from algotrader.tools import *


current_time = datetime.datetime.now()


class Event(Atom):
    def on(self, handler):
        pass

    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "%s(%s)" % (self.__class__.__name__, ', '.join(items))


class EventHandler(Observer):
    __metaclass__ = abc.ABCMeta

    def on_next(self, event):
        event.on(self)

    def on_error(self, e):
        logger.debug("[%s] Error: %s" % (self.__class__.__name__, e))

    def on_completed(self):
        logger.debug("[%s] Completed" % self.__class__.__name__)
