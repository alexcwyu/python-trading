from algotrader.event.market_data import Bar, BarType, BarSize


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
        super(HistDataSubscriptionKey, self).__init__(inst_id=inst_id, provider_id=provider_id, data_type=data_type,
                                                      bar_type=bar_type, bar_size=bar_size)
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
        super(HistDataSubscriptionKey, self).__init__(inst_id=inst_id, provider_id=provider_id, data_type=data_type,
                                                      bar_type=bar_type, bar_size=bar_size)
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