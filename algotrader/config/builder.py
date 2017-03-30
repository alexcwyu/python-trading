from algotrader.config.app import *
from algotrader.config.broker import *
from algotrader.config.feed import *
from algotrader.config.config import *
from algotrader.config.persistence import *

from algotrader.provider.persistence import PersistenceMode
from algotrader.provider.persistence.data_store import DataStore

def realtime_mongo_persistance_config():
    return PersistenceConfig("realtime_mongo",
                      DataStore.Mongo, PersistenceMode.RealTime,
                      DataStore.Mongo, PersistenceMode.RealTime,
                      DataStore.Mongo, PersistenceMode.RealTime,
                      DataStore.Mongo, PersistenceMode.RealTime)

def backtest_mongo_persistance_config():
    return PersistenceConfig("backtest_mongo",
                             ref_ds_id=DataStore.Mongo, ref_persist_mode=PersistenceMode.Disable,
                             trade_ds_id=DataStore.Mongo, trade_persist_mode=PersistenceMode.Batch,
                             ts_ds_id=DataStore.Mongo, ts_persist_mode=PersistenceMode.Disable,
                             seq_ds_id=DataStore.Mongo, seq_persist_mode=PersistenceMode.Disable)


def backtest_in_memory_config():
    return PersistenceConfig("backtest_memory",
                             ref_ds_id=DataStore.Mongo, ref_persist_mode=PersistenceMode.Disable,
                             trade_ds_id=DataStore.InMemoryDB, trade_persist_mode=PersistenceMode.Disable,
                             ts_ds_id=DataStore.InMemoryDB, ts_persist_mode=PersistenceMode.Disable,
                             seq_ds_id=DataStore.InMemoryDB, seq_persist_mode=PersistenceMode.Disable)
