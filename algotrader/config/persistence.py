import abc

from algotrader.config.config import Config
from algotrader.provider.persistence import PersistenceMode


class PersistenceConfig(Config):
    __slots__ = (
        'ref_ds_id',
        'ref_persist_mode',

        'trade_ds_id',
        'trade_persist_mode',

        'ts_ds_id',
        'ts_persist_mode',

        'seq_ds_id',
        'seq_persist_mode',
    )

    def __init__(self, id=None,
                 ref_ds_id=None, ref_persist_mode=PersistenceMode.Disable,
                 trade_ds_id=None, trade_persist_mode=PersistenceMode.Disable,
                 ts_ds_id=None, ts_persist_mode=PersistenceMode.Disable,
                 seq_ds_id=None, seq_persist_mode=PersistenceMode.Disable):
        super(PersistenceConfig, self).__init__(id)
        self.ref_ds_id = ref_ds_id
        self.ref_persist_mode = ref_persist_mode
        self.trade_ds_id = trade_ds_id
        self.trade_persist_mode = trade_persist_mode
        self.ts_ds_id = ts_ds_id
        self.ts_persist_mode = ts_persist_mode
        self.seq_ds_id = seq_ds_id
        self.seq_persist_mode = seq_persist_mode


class DataStoreConfig(Config):
    __metaclass__ = abc.ABCMeta


class CassandraConfig(DataStoreConfig):
    __slots__ = (
        'contact_points',
        'port',
        'username',
        'password',
        'keyspace'
    )

    def __init__(self, id='Cassandra', contact_points=["127.0.0.1"], port=9042, username=None, password=None,
                 keyspace='algotrader'):
        super(CassandraConfig, self).__init__(id)
        self.contact_points = contact_points
        self.port = port
        self.username = username
        self.password = password
        self.keyspace = keyspace


class InfluxDBConfig(DataStoreConfig):
    __slots__ = (
        'host',
        'port',
        'username',
        'password',
        'dbname'
    )

    def __init__(self, id='Influx', host='localhost', port=8086, username='root', password='root', dbname='algotrader'):
        super(InfluxDBConfig, self).__init__(id)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname


class MongoDBConfig(DataStoreConfig):
    __slots__ = (
        'host',
        'port',
        'username',
        'password',
        'dbname'
    )

    def __init__(self, id='Mongo', host='localhost', port=27017, username=None, password=None, dbname='algotrader'):
        super(MongoDBConfig, self).__init__(id)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname


class KDBConfig(DataStoreConfig):
    __slots__ = (
        'host',
        'port',
        'username',
        'password'
    )

    def __init__(self, id='KDB', host='localhost', port=5000, username=None, password=None):
        super(KDBConfig, self).__init__(id)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
