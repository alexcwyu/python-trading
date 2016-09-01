from algotrader.provider.persistence.persist import DataStore
from algotrader.provider.provider import ProviderManager


class DataStoreManager(ProviderManager):
    def __init__(self):
        super(DataStoreManager, self).__init__()
        pass

    def register(self, datastore):
        if datastore and isinstance(datastore, DataStore):
            super(DataStoreManager, self).register(datastore)