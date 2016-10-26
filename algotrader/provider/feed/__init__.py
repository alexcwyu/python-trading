import abc

from algotrader.provider import Provider


class Feed(Provider):
    CSV = "CSV"
    PandasMemory = "PandasMemory"
    Yahoo = "Yahoo"
    Google = "Google"
    Quandl = "Quandl"

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Provider, self).__init__()

    def subscribe_all_mktdata(self, sub_keys):
        for sub_key in sub_keys:
            self.subscribe_mktdata(sub_key)

    def unsubscribe_all_mktdata(self, sub_keys):
        for sub_key in sub_keys:
            self.unsubscribe_mktdata(sub_key)

    @abc.abstractmethod
    def subscribe_mktdata(self, sub_key):
        raise NotImplementedError()

    @abc.abstractmethod
    def unsubscribe_mktdata(self, sub_key):
        raise NotImplementedError()
