from algotrader.config.config import Config
from algotrader.config.persistence import PersistenceConfig
from algotrader.config.trading import TradingConfig
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock
from datetime import date


class ApplicationConfig(Config):
    __slots__ = (

        'ref_data_mgr_type',
        'clock_type',
        'persistence_config',
        'trading_config',
        'configs',
    )

    def __init__(self, id=None,
                 ref_data_mgr_type=RefDataManager.InMemory,
                 clock_type=Clock.Simulation,
                 persistence_config=None,
                 *configs):
        super(ApplicationConfig, self).__init__(id)

        self.ref_data_mgr_type = ref_data_mgr_type
        self.clock_type = clock_type
        self.persistence_config = persistence_config if persistence_config else PersistenceConfig()
        self.trading_configs = []
        self.configs = {}

        for config in configs:
            if isinstance(config, TradingConfig):
                self.trading_configs.append(config)
            elif isinstance(config, TradingConfig):
                self.trading_configs.append(config)
            else:
                self.configs[config.__class__] = config

    def get_config(self, cls, create=True):
        return self._get_or_create_config(self.configs, cls, create)

    def get_trading_configs(self):
        return self.trading_configs

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
                 ref_data_mgr_type=RefDataManager.InMemory,
                 clock_type=Clock.Simulation,
                 feed_id=None,
                 instrument_ids=None, subscription_types=None,
                 persistence_config=None,
                 *configs):
        super(RealtimeMarketDataImporterConfig, self).__init__(id, ref_data_mgr_type, clock_type, persistence_config, configs)
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
                 ref_data_mgr_type=RefDataManager.InMemory,
                 feed_id=None,
                 instrument_ids=None, subscription_types=None,
                 from_date=date(2010, 1, 1), to_date=date.today(),
                 persistence_config=None,
                 *configs):
        super(HistoricalMarketDataImporterConfig, self).__init__(id, ref_data_mgr_type, Clock.Simulation, persistence_config, configs)
        self.feed_id = feed_id
        self.instrument_ids = instrument_ids
        self.subscription_types = subscription_types
        self.from_date = from_date
        self.to_date = to_date