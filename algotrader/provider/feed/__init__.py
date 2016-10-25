import abc

from algotrader.provider import Provider


class Feed(Provider):
    CSV = "CSV"
    PandasMemory = "PandasMemory"
    Yahoo = "Yahoo"
    Google = "Google"

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Provider, self).__init__()

    @abc.abstractmethod
    def subscribe_mktdata(self, *sub_key):
        raise NotImplementedError()

    @abc.abstractmethod
    def unsubscribe_mktdata(self, *sub_key):
        raise NotImplementedError()
