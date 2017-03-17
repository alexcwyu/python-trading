import abc

from algotrader.utils.ser_deser import Serializable

from algotrader.model.market_data_pb2 import Bar

class MarketDataType(object):
    Bar = 'Bar'
    Quote = 'Quote'
    Trade = 'Trade'
    MarketDepth = 'MarketDepth'


class BarSize(object):
    S1 = 1
    S5 = 5
    S15 = 15
    S30 = 30
    M1 = 60
    M5 = 5 * 60
    M15 = 15 * 60
    M30 = 30 * 60
    H1 = 60 * 60
    D1 = 24 * 60 * 60


class DataSubscriptionType(Serializable):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_type(self):
        raise NotImplementedError()

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, DataSubscriptionType):
            return False
        return (self.get_type()) == (other.get_type())


class BarSubscriptionType(DataSubscriptionType):
    __slots__ = (
        'bar_type',
        'bar_size'
    )

    def __init__(self, bar_type=Bar.Time, bar_size=BarSize.D1):
        self.bar_type = bar_type
        self.bar_size = bar_size

    def get_type(self):
        return MarketDataType.Bar

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, BarSubscriptionType):
            return False
        return (self.get_type(), self.bar_type, self.bar_size) == (other.get_type(), other.bar_type, other.bar_size)


class QuoteSubscriptionType(DataSubscriptionType):
    def get_type(self):
        return MarketDataType.Quote


class TradeSubscriptionType(DataSubscriptionType):
    def get_type(self):
        return MarketDataType.Trade


class MarketDepthSubscriptionType(DataSubscriptionType):
    __slots__ = (
        'num_rows',
        'provider_id'
    )

    def __init__(self, num_rows=1, provider_id=None):
        self.num_rows = num_rows
        self.provider_id = provider_id

    def get_type(self):
        raise MarketDataType.MarketDepth

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, MarketDepthSubscriptionType):
            return False
        return (self.get_type(), self.num_rows, self.provider_id) == (
            other.get_type(), other.num_rows, other.provider_id)

    def id(self):
        return "%s.%s" % (self.get_type(), self.num_rows)


class SubscriptionKey(object):
    __slots__ = (
        'provider_id',
        'inst_id',
        'subscription_type',
    )

    def __init__(self, inst_id, provider_id='IB', subscription_type=None):
        self.provider_id = provider_id
        self.inst_id = inst_id
        self.subscription_type = subscription_type if subscription_type else BarSubscriptionType(bar_type=Bar.Time,
                                                                                                 bar_size=BarSize.D1)

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, SubscriptionKey):
            return False

        return ((self.provider_id, self.inst_id, self.subscription_type) ==
                (other.provider_id, other.inst_id, other.subscription_type))


class HistDataSubscriptionKey(SubscriptionKey):
    __slots__ = (
        'from_date',
        'to_date',
    )

    def __init__(self, inst_id, provider_id='IB', subscription_type=None,
                 from_date=None, to_date=None):
        super(HistDataSubscriptionKey, self).__init__(inst_id=inst_id, provider_id=provider_id,
                                                      subscription_type=subscription_type)
        self.from_date = from_date
        self.to_date = to_date

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, HistDataSubscriptionKey):
            return False

        return ((self.provider_id, self.inst_id, self.subscription_type,
                 self.from_date, self.to_date) ==
                (other.provider_id, other.inst_id, other.subscription_type,
                 other.from_date, other.to_date))


class MarketDataSubscriber(object):
    def subscript_market_data(self, feed, instruments, subscription_types, from_date=None, to_date=None):
        for sub_key in self.get_subscription_keys(feed.id(), instruments, subscription_types, from_date, to_date):
            feed.subscribe_mktdata(sub_key)

    def get_subscription_keys(self, feed_id, instruments, subscription_types, from_date=None, to_date=None):
        keys = []
        for instrument in instruments:
            for subscription_type in subscription_types:
                if from_date and to_date:

                    keys.append(HistDataSubscriptionKey(inst_id=instrument.inst_id,
                                                        provider_id=feed_id,
                                                        subscription_type=subscription_type,
                                                        from_date=from_date,
                                                        to_date=to_date))

                else:
                    keys.append(SubscriptionKey(inst_id=instrument.inst_id,
                                                provider_id=feed_id,
                                                subscription_type=subscription_type))
                    # feed.subscribe_mktdata(sub_key)
        return keys
