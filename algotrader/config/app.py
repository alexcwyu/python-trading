from algotrader.config.config import Config
from algotrader.config.broker import BrokerConfig
from algotrader.config.feed import FeedConfig
from algotrader.config.persistence import PersistenceConfig
from algotrader.config.trading import TradingConfig


class ApplicationConfig(Config):
    __slots__ = (
        'ref_datastore_id',
        'trading_datastore_id',
        'time_series_datastore_id',
        'ref_data_mgr_type',
        'clock_type',
        'trading_configs'
        'broker_configs'
        'persistence_configs'
        'feed_configs'
    )

    def __init__(self, ref_datastore_id, trading_datastore_id, time_series_datastore_id, ref_data_mgr_type, clock_type, *configs):
        self.ref_datastore_id = ref_datastore_id
        self.time_series_datastore_id = time_series_datastore_id
        self.trading_datastore_id = trading_datastore_id

        self.ref_data_mgr_type = ref_data_mgr_type
        self.clock_type = clock_type

        self.trading_configs = []
        self.broker_configs = []
        self.persistence_configs = []
        self.feed_configs = []

        for config in configs:
            if isinstance(config, TradingConfig):
                self.trading_configs.append(config)
            elif isinstance(config, BrokerConfig):
                self.broker_configs.append(config)
            elif isinstance(config, PersistenceConfig):
                self.persistence_configs.append(config)
            elif isinstance(config, FeedConfig):
                self.feed_configs.append(config)
