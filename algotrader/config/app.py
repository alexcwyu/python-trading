from datetime import date

from algotrader.config.config import Config
from algotrader.config.persistence import PersistenceConfig
from algotrader.model.market_data_pb2 import Bar
from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import BarSubscriptionType, BarSize
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock


class ApplicationConfig(Config):
    __slots__ = (

        'ref_data_mgr_type',
        'clock_type',
        'persistence_config',
        'provider_configs',
    )

    def __init__(self, id=None,
                 ref_data_mgr_type=RefDataManager.InMemory,
                 clock_type=Clock.Simulation,
                 persistence_config=None,
                 provider_configs=None):
        super(ApplicationConfig, self).__init__(id)

        self.ref_data_mgr_type = ref_data_mgr_type
        self.clock_type = clock_type
        self.persistence_config = persistence_config if persistence_config else PersistenceConfig()
        self.provider_configs = {}

        if provider_configs:
            if not isinstance(provider_configs, (list, tuple)):
                self.provider_configs[provider_configs.__class__] = provider_configs
            else:
                for provider_config in provider_configs:
                    self.provider_configs[provider_config.__class__] = provider_config

    def get_config(self, cls, create=True):
        return self._get_or_create_config(self.provider_configs, cls, create)

    def _get_or_create_config(self, dict, cls, create=True):
        result = dict.get(cls, None)
        if result is None and create:
            result = cls()
        return result


class RealtimeMarketDataImporterConfig(ApplicationConfig):
    __slots__ = (
        'feed_id',
        'instrument_ids',
        'subscription_types',
    )

    def __init__(self, id=None,
                 feed_id=None,
                 instrument_ids=None, subscription_types=None,
                 ref_data_mgr_type=RefDataManager.InMemory,
                 clock_type=Clock.Simulation,
                 persistence_config=None,
                 provider_configs=None):
        super(RealtimeMarketDataImporterConfig, self).__init__(id, ref_data_mgr_type, clock_type, persistence_config,
                                                               provider_configs)
        self.feed_id = feed_id
        self.instrument_ids = instrument_ids
        self.subscription_types = subscription_types


class HistoricalMarketDataImporterConfig(ApplicationConfig):
    __slots__ = (
        'feed_id',
        'instrument_ids',
        'subscription_types',
        'from_date',
        'to_date',
    )

    def __init__(self, id=None,
                 feed_id=None,
                 instrument_ids=None, subscription_types=None,
                 from_date=date(2010, 1, 1), to_date=date.today(),
                 ref_data_mgr_type=RefDataManager.InMemory,
                 persistence_config=None,
                 provider_configs=None):
        super(HistoricalMarketDataImporterConfig, self).__init__(id, ref_data_mgr_type, Clock.Simulation,
                                                                 persistence_config, provider_configs)
        self.feed_id = feed_id
        self.instrument_ids = instrument_ids
        self.subscription_types = subscription_types
        self.from_date = from_date
        self.to_date = to_date


class TradingConfig(ApplicationConfig):
    __slots__ = (
        'stg_id',
        'stg_cls',
        'portfolio_id',
        'instrument_ids',
        'subscription_types',
        'feed_id',
        'broker_id',
        'stg_configs'

    )

    def __init__(self, id=None, stg_id=None, stg_cls=None, portfolio_id=None,
                 instrument_ids=None,
                 subscription_types=None,
                 feed_id=None, broker_id=None, stg_configs=None,
                 ref_data_mgr_type=RefDataManager.InMemory,
                 clock_type=Clock.Simulation,
                 persistence_config=None,
                 provider_configs=None):
        super(TradingConfig, self).__init__(id=id if id else stg_id, ref_data_mgr_type=ref_data_mgr_type,
                                            clock_type=clock_type, persistence_config=persistence_config,
                                            provider_configs=provider_configs)
        self.stg_id = stg_id
        self.stg_cls = stg_cls
        self.portfolio_id = portfolio_id

        self.instrument_ids = instrument_ids
        if not isinstance(self.instrument_ids, (list, tuple)):
            self.instrument_ids = [self.instrument_ids]

        self.subscription_types = subscription_types if subscription_types else [
            BarSubscriptionType(bar_type=Bar.Time, bar_size=BarSize.D1)]
        if not isinstance(self.subscription_types, (list, tuple)):
            self.subscription_types = [self.subscription_types]

        self.feed_id = feed_id
        self.broker_id = broker_id
        self.clock_type = clock_type
        self.stg_configs = stg_configs


class LiveTradingConfig(TradingConfig):
    def __init__(self, id=None, stg_id=None, stg_cls=None, portfolio_id=None,
                 instrument_ids=None,
                 subscription_types=None,
                 feed_id=Broker.IB, broker_id=Broker.IB, stg_configs=None,
                 ref_data_mgr_type=RefDataManager.DB,
                 persistence_config=None,
                 provider_configs=None):
        super(LiveTradingConfig, self).__init__(id=id, stg_id=stg_id, stg_cls=stg_cls, portfolio_id=portfolio_id,
                                                instrument_ids=instrument_ids,
                                                subscription_types=subscription_types,
                                                feed_id=feed_id, broker_id=broker_id,
                                                stg_configs=stg_configs,
                                                ref_data_mgr_type=ref_data_mgr_type,
                                                clock_type=Clock.RealTime,
                                                persistence_config=persistence_config,
                                                provider_configs=provider_configs)


class BacktestingConfig(TradingConfig):
    __slots__ = (
        'from_date',
        'to_date',
        'portfolio_initial_cash',
    )

    def __init__(self, id=None, stg_id=None, stg_cls=None, portfolio_id=None,
                 instrument_ids=None, subscription_types=None,
                 feed_id=Feed.CSV, broker_id=Broker.Simulator, from_date=date(2010, 1, 1), to_date=date.today(),
                 portfolio_initial_cash=1000000,
                 stg_configs=None,
                 ref_data_mgr_type=RefDataManager.DB,
                 persistence_config=None,
                 provider_configs=None):
        super(BacktestingConfig, self).__init__(id=id, stg_id=stg_id, stg_cls=stg_cls, portfolio_id=portfolio_id,
                                                instrument_ids=instrument_ids,
                                                subscription_types=subscription_types,
                                                feed_id=feed_id, broker_id=broker_id,
                                                stg_configs=stg_configs,
                                                ref_data_mgr_type=ref_data_mgr_type,
                                                clock_type=Clock.Simulation,
                                                persistence_config=persistence_config,
                                                provider_configs=provider_configs)
        self.portfolio_initial_cash = portfolio_initial_cash
        self.from_date = from_date
        self.to_date = to_date
