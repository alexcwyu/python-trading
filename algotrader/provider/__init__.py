import abc

from algotrader import SimpleManager


class Provider(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Provider, self).__init__()

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()


class ProviderManager(SimpleManager):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(ProviderManager, self).__init__()