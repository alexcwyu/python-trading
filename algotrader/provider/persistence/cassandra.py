from cassandra.cluster import Cluster

from algotrader.config.persistence import CassandraConfig
from algotrader.provider.persistence import DataStore


class CassandraDataStore(DataStore):
    def __init__(self, app_context):
        self.app_context = app_context
        self.cass_config = app_context.app_config.get_config(CassandraConfig)

    def _start(self):
        # TODO authentication provider
        self.cluster = Cluster(contact_points=self.cass_config.contact_points, port=self.cass_config.port)
        self.session = self.cluster.connect()

    def _stop(self):
        self.cluster.shutdown()

    def id(self):
        return DataStore.Cassandra

    def save_bar(self, bar):
        pass

    def save_quote(self, quote):
        pass

    def save_trade(self, trade):
        pass

    def save_market_depth(self, market_depth):
        pass

    def save_order(self, order):
        pass

    def save_portfolio(self, portfolio):
        pass

    def save_instrument(self, instrument):
        pass

    def save_time_series(self, timeseries):
        pass
