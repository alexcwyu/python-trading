import abc

from algotrader.event import OrderEventHandler


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


from algotrader.event.market_data import *


class SubscriptionKey(object):
    __slots__ = (
        'provider_id',
        'data_type',
        'inst_id',
        'bar_type',
        'bar_size'
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
        if not isinstance(other, SubscriptionKey):
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
        super(HistDataSubscriptionKey, self).__init__(inst_id=inst_id, provider_id=provider_id, data_type=data_type, bar_type=bar_type, bar_size=bar_size)
        self.from_date = from_date
        self.to_date = to_date

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, HistDataSubscriptionKey):
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
        super(HistDataSubscriptionKey, self).__init__(inst_id=inst_id, provider_id=provider_id, data_type=data_type, bar_type=bar_type, bar_size=bar_size)
        self.num_rows = num_rows

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, MarketDepthSubscriptionKey):
            return False

        return ((self.provider_id, self.data_type, self.inst_id, self.bar_type, self.bar_size,
                 self.num_rows) ==
                (other.provider_id, other.data_type, other.inst_id, other.bar_type, other.bar_size,
                 other.num_rows))


class ProviderManager(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.__mapping = {}

    def get(self, id):
        return self.__mapping.get(id, None)

    def register(self, provider):
        self.__mapping[provider.id()] = provider


class FeedManager(ProviderManager):
    def __init__(self):
        super(FeedManager, self).__init__()

    def register(self, provider):
        if provider and isinstance(provider, Feed):
            super(FeedManager, self).register(provider)


feed_mgr = FeedManager()


class BrokerManager(ProviderManager):
    def __init__(self):
        super(BrokerManager, self).__init__()
        pass

    def register(self, provider):
        if provider and isinstance(provider, Broker):
            super(BrokerManager, self).register(provider)


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
