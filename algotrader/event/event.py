import time

from algotrader.provider.persistence import Persistable

from algotrader import HasId

class Event(Persistable):
    __slots__ = (
        'timestamp'  # timestamp in unix timestamp millis sec
    )

    def __init__(self, timestamp=None):
        self.timestamp = timestamp if timestamp is not None else int(time.time() * 1000)

    def on(self, handler):
        pass
