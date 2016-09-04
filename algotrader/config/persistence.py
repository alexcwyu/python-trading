import abc

from algotrader.config.config import Config


class PersistenceConfig(Config):
    __metaclass__ = abc.ABCMeta


class CassandraConfig(PersistenceConfig):
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


class InfluxDBConfig(PersistenceConfig):
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


class MongoDBConfig(PersistenceConfig):
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


class KDBConfig(PersistenceConfig):
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
