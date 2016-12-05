import abc

from algotrader.provider.persistence import Persistable


class Config(Persistable):
    __metaclass__ = abc.ABCMeta
    __slots__ = (
        'config_id',
    )

    def __init__(self, config_id):
        self.config_id = config_id

    def id(self):
        return self.config_id
