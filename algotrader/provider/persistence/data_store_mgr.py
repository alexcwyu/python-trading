from algotrader.provider import ProviderManager
from algotrader.provider.persistence import DataStore
from algotrader.provider.persistence.cassandra import CassandraDataStore
from algotrader.provider.persistence.influx import InfluxDataStore
from algotrader.provider.persistence.kdb import KDBDataStore
from algotrader.provider.persistence.mongodb import MongoDBDataStore


class DataStoreManager(ProviderManager):
    def __init__(self, app_context):
        super(DataStoreManager, self).__init__()
        self.app_context = app_context

        self.add(CassandraDataStore())
        self.add(InfluxDataStore())
        self.add(KDBDataStore())
        self.add(MongoDBDataStore())

    def add(self, datastore):
        if datastore and isinstance(datastore, DataStore):
            super(DataStoreManager, self).add(datastore)

    def _start(self):
        self.app_config.persistence_configs
        ## TODO foreach config: init and start