from algotrader.provider.persistence.persist import DataStore

from pymongo import MongoClient

class MongoDBDataStore(DataStore):
    def __init__(self, config):
        self.config = config


    def start(self):
        client = MongoClient('localhost', 27017)
        db = client.market_data
        pass


    def stop(self):
        pass


