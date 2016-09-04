from influxdb import InfluxDBClient

from algotrader.provider.persistence.persist import DataStore


class InfluxDataStore(DataStore):
    def __init__(self, influx_config):
        self.influx_config = influx_config

    def start(self):
        if not self.started:
            self.client = InfluxDBClient(self.influx_config.host, self.influx_config.port, self.influx_config.username,
                                         self.influx_config.password,
                                         self.influx_config.dbname)
            self.started = True

    def stop(self):
        if self.started:
            # TODO
            self.started = False

    def id(self):
        return DataStore.Influx

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
