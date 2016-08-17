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
