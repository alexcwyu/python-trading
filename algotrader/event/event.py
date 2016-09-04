from algotrader.provider.persistence.persist import Persistable
from algotrader.utils.clock import realtime_clock


class Event(Persistable):
    __slots__ = (
        'timestamp'  # timestamp in unix timestamp millis sec
    )

    def __init__(self, timestamp=None):
        self.timestamp = timestamp if timestamp else realtime_clock.now()

    def on(self, handler):
        pass
