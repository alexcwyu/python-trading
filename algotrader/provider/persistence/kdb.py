from qpython import qconnection

from algotrader.config.persistence import KDBConfig
from algotrader.provider.persistence import DataStore


class KDBDataStore(DataStore):
    def __init__(self, app_context):
        super(KDBDataStore, self).__init__()
        self.app_context = app_context
        self.kdb_config = app_context.app_config.get_config(KDBConfig)

    def _start(self):
        self.q = qconnection.QConnection(host=self.kdb_config.host, port=self.kdb_config.port)

    def _stop(self):
        self.q.close()

    def id(self):
        return DataStore.KDB

    def load_all(self, clazz):
        raise NotImplementedError()


    # RefDataStore
    def save_instrument(self, instrument):
        raise NotImplementedError()

    def save_exchange(self, exchange):
        raise NotImplementedError()

    def save_currency(self, currency):
        raise NotImplementedError()

    # TimeSeriesDataStore
    def save_bar(self, bar):
        raise NotImplementedError()

    def save_quote(self, quote):
        raise NotImplementedError()

    def save_trade(self, trade):
        raise NotImplementedError()

    def save_market_depth(self, market_depth):
        raise NotImplementedError()

    def save_time_series(self, timeseries):
        raise NotImplementedError()

    # TradeDataStore
    def save_account(self, account):
        raise NotImplementedError()

    def save_portfolio(self, portfolio):
        raise NotImplementedError()

    def save_order(self, order):
        raise NotImplementedError()

    def save_strategy(self, strategy):
        raise NotImplementedError()

    def save_account_event(self, account_event):
        raise NotImplementedError()

    def save_order_event(self, order_event):
        raise NotImplementedError()

    def save_execution_event(self, execution_event):
        raise NotImplementedError()

    # SequenceDataStore
    def save_sequence(self, key, seq):
        raise NotImplementedError()
