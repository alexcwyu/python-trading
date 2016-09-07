from qpython import qconnection

from algotrader.provider.persistence import DataStore
from algotrader.config.persistence import KDBConfig


class KDBDataStore(DataStore):
    def __init__(self, app_context):
        self.app_context = app_context
        self.kdb_config = app_context.app_config.get_config(KDBConfig)

    def _start(self):
        self.q = qconnection.QConnection(host=self.kdb_config.host, port=self.kdb_config.port)

    def _stop(self):
        self.q.close()

    def id(self):
        return DataStore.KDB

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
