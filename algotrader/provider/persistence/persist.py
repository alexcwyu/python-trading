import abc

from algotrader.provider.provider import Provider


class Query():
    __metaclass__ = abc.ABCMeta


class DataStore(Provider):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def query(self, query):
        raise NotImplementedError()

    def save(self, persistable):
        persistable.save(self)


class Persistable:
    def save(self, data_store):
        pass

    def load(self):
        pass
