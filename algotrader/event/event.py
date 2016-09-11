from algotrader.provider.persistence import Persistable
import datetime

class Event(Persistable):
    __slots__ = (
        'timestamp'  # timestamp in unix timestamp millis sec
    )

    def __init__(self, timestamp=None):
        self.timestamp = timestamp if timestamp else datetime.datetime.now()

    def on(self, handler):
        pass
