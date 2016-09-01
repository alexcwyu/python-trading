import abc

from algotrader.event.market_data import Bar, BarType, BarSize, MarketDataType


class DataSubscriptionType(object):
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

    def __init__(self, bar_type=BarType.Time, bar_size=BarSize.D1):
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
        'num_rows'
    )

    def __init__(self, num_rows=1):
        self.num_rows = num_rows


    def get_type(self):
        raise MarketDataType.MarketDepth

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, MarketDepthSubscriptionType):
            return False
        return (self.get_type(), self.num_rows) == (other.get_type(), other.num_rows)


class SubscriptionKey(object):
    __slots__ = (
        'provider_id',
        'inst_id',
        'subscription_type',
    )

    def __init__(self, inst_id, provider_id='IB', subscription_type=None):
        self.provider_id = provider_id
        self.inst_id = inst_id
        self.subscription_type = subscription_type if subscription_type else BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)

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
        super(HistDataSubscriptionKey, self).__init__(inst_id=inst_id, provider_id=provider_id, subscription_type=subscription_type)
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

