from qpython import qconnection

from algotrader.provider.persistence.persist import DataStore


class KDBDataStore(DataStore):
    def __init__(self, kdb_config):
        self.kdb_config = kdb_config

    def start(self):
        if not self.started:
            self.q = qconnection.QConnection(host=self.kdb_config.host, port=self.kdb_config.port)
            self.started = True

    def stop(self):
        if self.started:
            self.q.close()
            self.started = False

    def id(self):
        return DataStore.KDB

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
