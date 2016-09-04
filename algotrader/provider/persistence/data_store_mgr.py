from algotrader.provider.persistence.persist import DataStore
from algotrader.provider.provider import ProviderManager


class DataStoreManager(ProviderManager):
    def __init__(self, app_context):
        super(DataStoreManager, self).__init__()
        self.app_context = app_context

    def add(self, datastore):
        if datastore and isinstance(datastore, DataStore):
            super(DataStoreManager, self).add(datastore)


    def _start(self):
        self.app_config.persistence_configs
        ## TODO foreach config: init and start