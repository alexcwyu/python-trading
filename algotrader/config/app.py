from algotrader.config.config import Config
from algotrader.config.persistence import PersistenceConfig
from algotrader.config.trading import TradingConfig
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock


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
