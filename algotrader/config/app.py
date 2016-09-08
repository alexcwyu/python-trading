from algotrader.config.config import Config
from algotrader.config.trading import TradingConfig


class ApplicationConfig(Config):
    __slots__ = (
        'ref_datastore_id',
        'trade_datastore_id',
        'time_series_datastore_id',
        'seq_datastore_id',

        'ref_data_mgr_type',
        'clock_type',

        'trading_configs',
        # 'broker_configs',
        # 'persistence_configs',
        # 'feed_configs',
        'configs',
    )

    def __init__(self, id,
                 ref_datastore_id,
                 trade_datastore_id,
                 time_series_datastore_id,
                 seq_datastore_id,
                 ref_data_mgr_type,
                 clock_type,
                 *configs):
        super(ApplicationConfig, self).__init__(id)
        self.ref_datastore_id = ref_datastore_id
        self.time_series_datastore_id = time_series_datastore_id
        self.trade_datastore_id = trade_datastore_id
        self.seq_datastore_id = seq_datastore_id

        self.ref_data_mgr_type = ref_data_mgr_type
        self.clock_type = clock_type

        # self.trading_configs = {}
        # self.broker_configs = {}
        # self.persistence_configs = {}
        # self.feed_configs = {}
        self.configs = {}

        for config in configs:
            if isinstance(config, TradingConfig):
                self.trading_configs[config.stg_id] = config
            else:
                self.configs[config.__class__] = config

            # elif isinstance(config, BrokerConfig):
            #     self.broker_configs[config.__class__.__name__] = config
            # elif isinstance(config, PersistenceConfig):
            #     self.persistence_configs[config.__class__.__name__] = config
            # elif isinstance(config, FeedConfig):
            #     self.feed_configs[config.__class__.__name__] = config

    # def get_trading_config(self, cls, create=True):
    #     return self._get_or_create_config(self.trading_configs, cls, create)
    #
    # def get_broker_config(self, cls, create=True):
    #     return self._get_or_create_config(self.broker_configs, cls, create)
    #
    # def get_persistence_config(self, cls, create=True):
    #     return self._get_or_create_config(self.persistence_configs, cls, create)
    #
    # def get_feed_config(self, cls, create=True):
    #     return self._get_or_create_config(self.feed_configs, cls, create)

    def get_config(self, cls, create=True):
        return self._get_or_create_config(self.configs, cls, create)

    def get_trading_config(self, stg_id, default = None):
        return self.trading_configs.get(stg_id, default)

    def _get_or_create_config(self, dict, cls, create=True):
        result = dict.get(cls, None)
        if result is None and create:
            result = cls()
        return result
