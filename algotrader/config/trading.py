import abc
from datetime import date

from algotrader.config.config import Config
from algotrader.event.market_data import BarType, BarSize
from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock


class TradingConfig(Config):
    __metaclass__ = abc.ABCMeta

    __slots__ = (
        'stg_id',
        'portfolio_id',
        'instrument_ids',
        'subscription_types',
        'feed_id',
        'broker_id',
        'ref_data_mgr_type',
        'clock_type',
        'stg_configs'

    )

    def __init__(self, id, stg_id, portfolio_id,
                 subscription_types,
                 instrument_ids,
                 feed_id, broker_id,
                 ref_data_mgr_type, clock_type, stg_configs):
        super(TradingConfig, self).__init__(id=id if id else stg_id)
        self.stg_id = stg_id
        self.portfolio_id = portfolio_id

        self.instrument_ids = instrument_ids
        if not isinstance(self.instrument_ids, (list, tuple)):
            self.instrument_ids = [self.instrument_ids]

        self.subscription_types = subscription_types if subscription_types else [
            BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)]
        if not isinstance(self.subscription_types, (list, tuple)):
            self.subscription_types = [self.subscription_types]

        self.feed_id = feed_id
        self.broker_id = broker_id
        self.ref_data_mgr_type = ref_data_mgr_type
        self.clock_type = clock_type
        self.stg_configs = stg_configs

    def get_stg_configs_val(self, key, default_value=None):
        if self.stg_configs:
            return self.stg_configs.get(key, default_value)
        return default_value


class LiveTradingConfig(TradingConfig):
    def __init__(self, id=None, stg_id=None, portfolio_id=None, instrument_ids=None, subscription_types=None,
                 feed_id=Broker.IB, broker_id=Broker.IB,
                 ref_data_mgr_type=RefDataManager.InMemory, stg_configs=None):
        super(LiveTradingConfig, self).__init__(id=id, stg_id=stg_id, portfolio_id=portfolio_id,
                                                instrument_ids=instrument_ids,
                                                subscription_types=subscription_types,
                                                feed_id=feed_id, broker_id=broker_id,
                                                ref_data_mgr_type=ref_data_mgr_type, clock_type=Clock.RealTime,
                                                stg_configs=stg_configs)


class BacktestingConfig(TradingConfig):
    __slots__ = (
        'from_date',
        'to_date',
    )

    def __init__(self, id=None, stg_id=None, portfolio_id=None, instrument_ids=None, subscription_types=None,
                 from_date=date(2010, 1, 1), to_date=date.today(),
                 feed_id=Feed.CSV, broker_id=Broker.Simulator,
                 ref_data_mgr_type=RefDataManager.InMemory, stg_configs=None):
        super(BacktestingConfig, self).__init__(id=id, stg_id=stg_id, portfolio_id=portfolio_id,
                                                instrument_ids=instrument_ids,
                                                subscription_types=subscription_types,
                                                feed_id=feed_id, broker_id=broker_id,
                                                ref_data_mgr_type=ref_data_mgr_type, clock_type=Clock.Simulation,
                                                stg_configs=stg_configs)
        self.from_date = from_date
        self.to_date = to_date
