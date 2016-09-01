import abc

from algotrader.provider.persistence.persist import Persistable


class Config(Persistable):
    __metaclass__ = abc.ABCMeta