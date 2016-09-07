from influxdb import InfluxDBClient

from algotrader.provider.persistence import DataStore
from algotrader.config.persistence import InfluxDBConfig


class InfluxDataStore(DataStore):
    def __init__(self, app_context):
        self.app_context = app_context
        self.influx_config = app_context.app_config.get_config(InfluxDBConfig)

    def _start(self):
        self.client = InfluxDBClient(self.influx_config.host, self.influx_config.port, self.influx_config.username,
                                     self.influx_config.password,
                                     self.influx_config.dbname)

    def _stop(self):
        # TODO
        pass

    def id(self):
        return DataStore.Influx

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
