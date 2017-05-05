import abc

from algotrader.provider import Provider


class Feed(Provider):
    CSV = "CSV"
    PandasMemory = "PandasMemory"
    PandasH5 = "PandasH5"
    Yahoo = "Yahoo"
    Google = "Google"
    Quandl = "Quandl"

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Provider, self).__init__()

    @abc.abstractmethod
    def subscribe_mktdata(self, *sub_req):
        raise NotImplementedError()

    @abc.abstractmethod
    def unsubscribe_mktdata(self, *sub_req):
        raise NotImplementedError()

    def _get_feed_config(self, path: str, default=None):
        return self.app_context.app_config.get_feed_config(self.id(), path, default=default)
