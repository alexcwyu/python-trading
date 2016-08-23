from influxdb import InfluxDBClient

from algotrader.provider.persistence.persist import DataStore


class InfluxDataStore(DataStore):
    def __init__(self, config):
        self.config = config

    def stop(self):
        pass

    def start(self):
        host = 'pinheads-hueylewis-1.c.influxdb.com'
        port = 8083
        username = 'readonly'
        password = '11111111'
        dbname = 'hsi'
        self.client = InfluxDBClient(host, port, username, password, dbname)

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
