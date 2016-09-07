from influxdb import InfluxDBClient

from algotrader.config.persistence import InfluxDBConfig
from algotrader.provider.persistence import DataStore


class InfluxDataStore(DataStore):
    def __init__(self, app_context):
        super(InfluxDataStore, self).__init__()
        self.app_context = app_context
        self.influx_config = app_context.app_config.get_config(InfluxDBConfig)

    def _start(self):
        self.client = InfluxDBClient(self.influx_config.host, self.influx_config.port, self.influx_config.username,
                                     self.influx_config.password,
                                     self.influx_config.dbname)

    def _stop(self):
        pass

    def id(self):
        return DataStore.Influx

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

