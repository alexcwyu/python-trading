from algotrader.utils.clock import realtime_clock
from algotrader.utils.ser_deser import Serializable

from algotrader.provider.persistence.persist import Persistable

class Event(Serializable, Persistable):
    __slots__ = (
        'timestamp'   # timestamp in unix timestamp millis sec
    )

    def __init__(self, timestamp=None):
        self.timestamp = timestamp if timestamp else realtime_clock.now()

    def on(self, handler):
        pass

    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "%s(%s)" % (self.__class__.__name__, ', '.join(items))
