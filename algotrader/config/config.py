import abc

from algotrader.provider.persistence import Persistable


class Config(Persistable):
    __metaclass__ = abc.ABCMeta
    __slots__ = (
        'id'
    )

    def __init__(self, id):
        self.id = id

    def id(self):
        return self.id
