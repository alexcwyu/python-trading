import abc

from algotrader import Startable, HasId


class Provider(Startable, HasId):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Provider, self).__init__()


from algotrader import SimpleManager

from algotrader.provider.broker.ib.ib_broker import IBBroker
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.feed.csv import CSVDataFeed
from algotrader.provider.feed.pandas_web import PandasWebDataFeed
from algotrader.provider.feed.pandas_memory import PandasMemoryDataFeed
from algotrader.provider.feed.pandas_db import PandaDBDataFeed
from algotrader.provider.datastore.inmemory import InMemoryDataStore
from algotrader.provider.datastore.mongodb import MongoDBDataStore


class ProviderManager(SimpleManager):
    def __init__(self):
        super(ProviderManager, self).__init__()

        self.add(Simulator())
        self.add(IBBroker())

        self.add(MongoDBDataStore())
        self.add(InMemoryDataStore())

        self.add(CSVDataFeed())
        self.add(PandasWebDataFeed())
        self.add(PandasMemoryDataFeed())
        self.add(PandaDBDataFeed())

    def id(self):
        return "ProviderManager"
