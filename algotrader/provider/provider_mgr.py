import abc

from algotrader import SimpleManager

from algotrader.provider.feed.csv_feed import CSVDataFeed
from algotrader.provider.feed.pandas_memory import PandasMemoryDataFeed
from algotrader.provider.feed.pandas_web import GoogleDataFeed, YahooDataFeed

from algotrader.provider.persistence.cassandra import CassandraDataStore
from algotrader.provider.persistence.influx import InfluxDataStore
from algotrader.provider.persistence.kdb import KDBDataStore
from algotrader.provider.persistence.mongodb import MongoDBDataStore

from algotrader.provider.broker.ib.ib_broker import IBBroker
from algotrader.provider.broker.sim.simulator import Simulator


class ProviderManager(SimpleManager):

    def __init__(self, app_context):
        super(ProviderManager, self).__init__()
        self.app_context = app_context

        self.add(Simulator(app_context=app_context))
        self.add(IBBroker(app_context=app_context))


        self.add(CassandraDataStore(app_context=app_context))
        self.add(InfluxDataStore(app_context=app_context))
        self.add(KDBDataStore(app_context=app_context))
        self.add(MongoDBDataStore(app_context=app_context))

        self.add(CSVDataFeed(app_context=app_context))
        self.add(PandasMemoryDataFeed(app_context=app_context))
        self.add(GoogleDataFeed(app_context=app_context))
        self.add(YahooDataFeed(app_context=app_context))