from cassandra.cluster import Cluster

from algotrader.provider.persistence.persist import DataStore


class CassandraDataStore(DataStore):
    def __init__(self, cass_config):
        self.cass_config = cass_config

    def start(self):
        if not self.started:
            #TODO authentication provider
            self.cluster = Cluster(contact_points=self.cass_config.contact_points, port=self.cass_config.port)
            self.session = self.cluster.connect()
            self.started = True

    def stop(self):
        if self.started:
            self.cluster.shutdown()
            self.started = False

    def id(self):
        return DataStore.Cassandra

    def query(self, query):
        pass

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
