from cassandra.cluster import Cluster

from algotrader.config.persistence import CassandraConfig
from algotrader.provider.persistence import DataStore


class CassandraDataStore(DataStore):
    def __init__(self):
        super(CassandraDataStore, self).__init__()

    def _start(self, app_context, **kwargs):
        self.cass_config = app_context.app_config.get_config(CassandraConfig)
        self.cluster = Cluster(contact_points=self.cass_config.contact_points, port=self.cass_config.port)
        self.session = self.cluster.connect()

    def _stop(self):
        self.cluster.shutdown()

    def id(self):
        return DataStore.Cassandra

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

    def save_account_update(self, account_update):
        raise NotImplementedError()

    def save_portfolio_update(self, portfolio_update):
        raise NotImplementedError()

    def save_new_order_req(self, new_order_req):
        raise NotImplementedError()

    def save_ord_cancel_req(self, ord_cancel_req):
        raise NotImplementedError()

    def save_ord_replace_req(self, ord_replace_req):
        raise NotImplementedError()

    def save_exec_report(self, exec_report):
        raise NotImplementedError()

    def save_ord_status_upd(self, ord_status_upd):
        raise NotImplementedError()

    # SequenceDataStore
    def save_sequence(self, key, seq):
        raise NotImplementedError()
