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

    __slots__ = (
        'create_at_start',
        'delete_at_stop',
    )

    def __init__(self, id, create_at_start=False, delete_at_stop=False):
        super(DataStoreConfig, self).__init__(id)
        self.create_at_start = create_at_start
        self.delete_at_stop = delete_at_stop


class CassandraConfig(DataStoreConfig):
    __slots__ = (
        'contact_points',
        'port',
        'username',
        'password',
        'keyspace',
        'cql_script_path'
    )

    def __init__(self, id='Cassandra', contact_points=["127.0.0.1"], port=9042, username=None, password=None,
                 keyspace='algotrader', cql_script_path='../../../scripts/cassandra/algotrader.cql',
                 create_at_start=False, delete_at_stop=False):
        super(CassandraConfig, self).__init__(id, create_at_start, delete_at_stop)
        self.contact_points = contact_points
        self.port = port
        self.username = username
        self.password = password
        self.keyspace = keyspace
        self.cql_script_path = cql_script_path


class InfluxDBConfig(DataStoreConfig):
    __slots__ = (
        'host',
        'port',
        'username',
        'password',
        'dbname'
    )

    def __init__(self, id='Influx', host='localhost', port=8086, username='root', password='root', dbname='algotrader',
                 create_at_start=False, delete_at_stop=False):
        super(InfluxDBConfig, self).__init__(id, create_at_start, delete_at_stop)
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

    def __init__(self, id='Mongo', host='localhost', port=27017, username=None, password=None, dbname='algotrader',
                 create_at_start=False, delete_at_stop=False):
        super(MongoDBConfig, self).__init__(id, create_at_start, delete_at_stop)
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

    def __init__(self, id='KDB', host='localhost', port=5000, username=None, password=None, create_at_start=False,
                 delete_at_stop=False):
        super(KDBConfig, self).__init__(id, create_at_start, delete_at_stop)
        self.host = host
        self.port = port
        self.username = username
        self.password = password


class InMemoryStoreConfig(DataStoreConfig):
    __slots__ = (
        'file'
    )

    def __init__(self, id='InMemory', file='algotrader_db.p', create_at_start=False,
                 delete_at_stop=False):
        super(InMemoryStoreConfig, self).__init__(id, create_at_start, delete_at_stop)
        self.file = file
