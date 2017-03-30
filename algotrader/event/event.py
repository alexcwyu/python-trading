import time

from algotrader.provider.persistence import Persistable


class Event(Persistable):
    __slots__ = (
        'timestamp',  # timestamp in unix timestamp millis sec
                      # the comma attached is important even it has only one element,
                      # for some reason use chain.from_iterable to query derived class this
                      # string will breakdown into list/tuple of single char since
                      # ('a') is not a valid one element tuple
                      # see https://wiki.python.org/moin/TupleSyntax
    )

    def __init__(self, timestamp=None):
        self.timestamp = timestamp if timestamp is not None else int(time.time() * 1000)

    def on(self, handler):
        pass
