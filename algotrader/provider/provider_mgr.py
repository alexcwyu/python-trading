from algotrader import SimpleManager
from algotrader.provider.broker.ib.ib_broker import IBBroker
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.feed.csv_feed import CSVDataFeed
from algotrader.provider.feed.pandas_memory import PandasMemoryDataFeed
from algotrader.provider.feed.pandas_web import GoogleDataFeed, YahooDataFeed
from algotrader.provider.persistence.cass import CassandraDataStore
from algotrader.provider.persistence.influx import InfluxDataStore
from algotrader.provider.persistence.inmemory import InMemoryDataStore
from algotrader.provider.persistence.kdb import KDBDataStore
from algotrader.provider.persistence.mongodb import MongoDBDataStore


class ProviderManager(SimpleManager):
    def __init__(self):
        super(ProviderManager, self).__init__()

        self.add(Simulator())
        self.add(IBBroker())

        self.add(CassandraDataStore())
        self.add(InfluxDataStore())
        self.add(KDBDataStore())
        self.add(MongoDBDataStore())
        self.add(InMemoryDataStore())

        self.add(CSVDataFeed())
        self.add(PandasMemoryDataFeed())
        self.add(GoogleDataFeed())
        self.add(YahooDataFeed())

    def id(self):
        return "ProviderManager"
