import abc

from algotrader import Startable

class Provider(Startable):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Provider, self).__init__()

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()


