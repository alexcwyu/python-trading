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


from algotrader.event.market_data import *


class SubscriptionKey:
    __slots__ = (
        'provider_id',
        'data_type',
        'inst_id',
        'bar_type',
        'bar_size',
        'from_date',
        'to_date',
    )

    def __init__(self, inst_id, provider_id='IB', data_type=Bar, bar_type=BarType.Time, bar_size=BarSize.D1):
        self.provider_id = provider_id
        self.data_type = data_type
        self.inst_id = inst_id
        self.bar_type = bar_type
        self.bar_size = bar_size

    def __eq__(self, other):
        if not other:
            return False
        if isinstance(other, SubscriptionKey):
            return False

        return ((self.provider_id, self.data_type, self.inst_id, self.bar_type, self.bar_size) ==
                (other.provider_id, other.data_type, other.inst_id, other.bar_type, other.bar_size))


class HistDataSubscriptionKey(SubscriptionKey):
    __slots__ = (
        'from_date',
        'to_date',
    )

    def __init__(self, inst_id, provider_id='IB', data_type=Bar, bar_type=BarType.Time, bar_size=BarSize.D1,
                 from_date=None, to_date=None):
        self.provider_id = provider_id
        self.data_type = data_type
        self.inst_id = inst_id
        self.bar_type = bar_type
        self.bar_size = bar_size
        self.from_date = from_date
        self.to_date = to_date

    def __eq__(self, other):
        if not other:
            return False
        if isinstance(other, HistDataSubscriptionKey):
            return False

        return ((self.provider_id, self.data_type, self.inst_id, self.bar_type, self.bar_size,
                 self.from_date, self.to_date) ==
                (other.provider_id, other.data_type, other.inst_id, other.bar_type, other.bar_size,
                 other.from_date, other.to_date))


class MarketDepthSubscriptionKey(SubscriptionKey):
    __slots__ = (
        'num_rows'
    )

    def __init__(self, inst_id, provider_id='IB', data_type=Bar, bar_type=BarType.Time, bar_size=BarSize.D1,
                 num_rows=1):
        self.provider_id = provider_id
        self.data_type = data_type
        self.inst_id = inst_id
        self.bar_type = bar_type
        self.bar_size = bar_size
        self.num_rows = num_rows

    def __eq__(self, other):
        if not other:
            return False
        if isinstance(other, MarketDepthSubscriptionKey):
            return False

        return ((self.provider_id, self.data_type, self.inst_id, self.bar_type, self.bar_size,
                 self.num_rows) ==
                (other.provider_id, other.data_type, other.inst_id, other.bar_type, other.bar_size,
                 other.num_rows))


class Feed(Provider):
    __metaclass__ = abc.ABCMeta

    def subscribe_mktdata(self, sub_key):
        pass

    def unsubscribe_mktdata(self, sub_key):
        pass

    def subscribe_hist_data(self, sub_key):
        pass

    def unsubscribe_hist_data(self, sub_key):
        pass


class FeedManager(object):
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


class BrokerManager(object):
    def __init__(self):
        self.__broker_mapping = {}

    def get_broker(self, broker_id):
        if broker_id in self.__broker_mapping:
            return self.__broker_mapping[broker_id]
        return None

    def reg_broker(self, broker):
        self.__broker_mapping[broker.id()] = broker


broker_mgr = BrokerManager()
