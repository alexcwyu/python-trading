import abc

from algotrader import SimpleManager
from algotrader.event.event_handler import OrderEventHandler


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


class FeedManager(ProviderManager):
    def __init__(self, app_context):
        super(FeedManager, self).__init__()
        self.app_context = app_context

    def add(self, provider):
        if provider and isinstance(provider, Feed):
            super(FeedManager, self).add(provider)


feed_mgr = FeedManager()


class BrokerManager(ProviderManager):
    def __init__(self, app_context):
        super(BrokerManager, self).__init__()
        self.app_context = app_context

    def add(self, provider):
        if provider and isinstance(provider, Broker):
            super(BrokerManager, self).add(provider)


broker_mgr = BrokerManager()


class Feed(Provider):
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


class Broker(Provider, OrderEventHandler):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Provider, self).__init__()
