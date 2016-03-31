import datetime

from rx.observable import Observer

from algotrader.utils import logger
from algotrader.utils.ser_deser import Serializable
current_time = datetime.datetime.now()



class Event(Serializable):
    def on(self, handler):
        pass

    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "%s(%s)" % (self.__class__.__name__, ', '.join(items))


class EventHandler(Observer):
    def on_next(self, event):
        event.on(self)

    def on_error(self, e):
        logger.debug("[%s] Error: %s" % (self.__class__.__name__, e))

    def on_completed(self):
        logger.debug("[%s] Completed" % self.__class__.__name__)
