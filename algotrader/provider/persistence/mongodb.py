from pymongo import MongoClient

from algotrader.provider.persistence.persist import RefDataStore, TradeDataStore, TimeSeriesDataStore

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.utils.ser_deser import JsonSerializer


class MongoDBDataStore(RefDataStore, TradeDataStore, TimeSeriesDataStore):
    def __init__(self, config):
        self.config = config

    def start(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['algotrader']

        self.bars = self.db['bars']
        self.trades = self.db['trades']
        self.quotes = self.db['quotes']
        self.trades = self.db['trades']
        self.market_depths = self.db['market_depths']
        self.time_series = self.db['time_series']

        self.instruments = self.db['instruments']
        self.currencies = self.db['currencies']
        self.exchanges = self.db['exchanges']

        self.accounts = self.db['accounts']
        self.portfolios = self.db['portfolios']
        self.orders = self.db['orders']
        self.strategies = self.db['strategies']

        self.order_events = self.db['order_events']
        self.acct_events = self.db['acct_events']
        self.execution_events = self.db['execution_events']
        self.strategies = self.db['strategies']
        self.serializer = JsonSerializer()

    def stop(self):
        pass

    def id(self):
        return "Mongo"

    def query(self, query):
        pass

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
        packed = bar.serialize()
        id = bar.id()
        self.bars.update({'_id': id}, packed, upsert=True)


    def save_quote(self, quote):
        packed = quote.serialize()
        id = quote.id()
        self.quotes.update({'_id': id}, packed, upsert=True)

    def save_trade(self, trade):
        packed = trade.serialize()
        id = trade.id()
        self.trades.update({'_id': id}, packed, upsert=True)

    def save_market_depth(self, market_depth):
        packed = market_depth.serialize()
        id = market_depth.id()
        self.market_depths.update({'_id': id}, packed, upsert=True)

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