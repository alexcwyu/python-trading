import abc

from algotrader.event import OrderEventHandler


class Provider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()


class Feed(Provider):
    __metaclass__ = abc.ABCMeta


class FeedManager():
    def __init__(self):
        self.__feed_mapping = {}

    def get_broker(self, feed_id):
        if feed_id in self.__feed_mapping:
            return self.__feed_mapping[feed_id]
        return None

    def reg_broker(self, feed):
        self.__feed_mapping[feed.id()] = feed


feed_mgr = FeedManager()


class Broker(Provider, OrderEventHandler):
    __metaclass__ = abc.ABCMeta


class BrokerManager():
    def __init__(self):
        self.__broker_mapping = {}

    def get_broker(self, broker_id):
        if broker_id in self.__broker_mapping:
            return self.__broker_mapping[broker_id]
        return None

    def reg_broker(self, broker):
        self.__broker_mapping[broker.id()] = broker


broker_mgr = BrokerManager()