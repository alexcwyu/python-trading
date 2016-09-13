import abc

from algotrader.config.config import Config


class PersistenceConfig(Config):
    __slots__ = (
        'ref_ds_id',
        'ref_persis_mode',

        'trade_ds_id',
        'trade_persis_mode',

        'ts_ds_id',
        'ts_persis_mode',

        'seq_ds_id',
        'seq_persis_mode',
    )

    def __init__(self, id,
                 ref_ds_id, ref_persis_mode,
                 trade_ds_id, trade_persis_mode,
                 ts_ds_id, ts_persis_mode,
                 seq_ds_id, seq_persis_mode):
        super(PersistenceConfig, self).__init__(id)
        self.ref_ds_id = ref_ds_id
        self.ref_persis_mode = ref_persis_mode
        self.trade_ds_id = trade_ds_id
        self.trade_persis_mode = trade_persis_mode
        self.ts_ds_id = ts_ds_id
        self.ts_persis_mode = ts_persis_mode
        self.seq_ds_id = seq_ds_id
        self.seq_persis_mode = seq_persis_mode


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
