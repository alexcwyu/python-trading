from pymongo import MongoClient

from algotrader.provider.persistence.persist import RefDataStore, TradeDataStore, TimeSeriesDataStore


class MongoDBDataStore(RefDataStore, TradeDataStore, TimeSeriesDataStore):
    def __init__(self, config):
        self.config = config

    def start(self):
        self.client = MongoClient('localhost', 27017)
        self.market_data_db = self.client.market_data

    def stop(self):
        pass

    def query(self, query):
        pass

    def load_all(self, clazz):
        raise NotImplementedError()

    def save_account(self, account):
        raise NotImplementedError()

    def save_portfolio(self, portfolio):
        raise NotImplementedError()

    def save_order(self, order):
        raise NotImplementedError()

    def save_instrument(self, instrument):
        raise NotImplementedError()

    def save_exchange(self, exchange):
        raise NotImplementedError()

    def save_currency(self, currency):
        raise NotImplementedError()

    def save_bar(self, bar):
        raise NotImplementedError()

    def save_quote(self, quote):
        raise NotImplementedError()

    def save_trade(self, trade):
        raise NotImplementedError()

    def save_market_depth(self, market_depth):
        raise NotImplementedError()

    def save_time_series(self, timeseries):
        pass
