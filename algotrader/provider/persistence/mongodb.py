from pymongo import MongoClient

from algotrader.provider.persistence.persist import RefDataStore, TradeDataStore, TimeSeriesDataStore, DataStore
from algotrader.utils.ser_deser import MapSerializer


class MongoDBDataStore(RefDataStore, TradeDataStore, TimeSeriesDataStore):
    def __init__(self, mongo_config):
        self.mongo_config = mongo_config
        self.started = False

    def start(self):
        if not self.started:
            self.client = MongoClient(host=self.mongo_config.host, port=self.mongo_config.port)
            self.db = self.client[self.mongo_config.dbname]

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
            self.serializer = MapSerializer

            self.started = True

    def stop(self):
        if self.started:
            # TODO
            self.started = False

    def id(self):
        return DataStore.Mongo

    def query(self, query):
        pass

    def load_all(self, clazz):
        result = []
        for data in self.db[clazz].find():
            obj = self.serializer.deserialize(data)
            # obj = clazz()
            # obj.deserialize(result)
            result.append(obj)
        return result

    def _serialize(self, serializable):
        return serializable.id(), self.serializer.serialize(serializable)
        # return serializable.id(), serializable.serialize()

    # RefDataStore
    def save_instrument(self, instrument):
        id, packed = self._serialize(instrument)
        self.instruments.update({'_id': id}, packed, upsert=True)

    def save_exchange(self, exchange):
        id, packed = self._serialize(exchange)
        self.exchanges.update({'_id': id}, packed, upsert=True)

    def save_currency(self, currency):
        id, packed = self._serialize(currency)
        self.currencies.update({'_id': id}, packed, upsert=True)

    # TimeSeriesDataStore
    def save_bar(self, bar):
        id, packed = self._serialize(bar)
        self.bars.update({'_id': id}, packed, upsert=True)

    def save_quote(self, quote):
        id, packed = self._serialize(quote)
        self.quotes.update({'_id': id}, packed, upsert=True)

    def save_trade(self, trade):
        id, packed = self._serialize(trade)
        self.trades.update({'_id': id}, packed, upsert=True)

    def save_market_depth(self, market_depth):
        id, packed = self._serialize(market_depth)
        self.market_depths.update({'_id': id}, packed, upsert=True)

    def save_time_series(self, timeseries):
        raise NotImplementedError()

    # TradeDataStore
    def save_account(self, account):
        id, packed = self._serialize(account)
        self.accounts.update({'_id': id}, packed, upsert=True)

    def save_portfolio(self, portfolio):
        id, packed = self._serialize(portfolio)
        self.portfolios.update({'_id': id}, packed, upsert=True)

    def save_order(self, order):
        id, packed = self._serialize(order)
        self.orders.update({'_id': id}, packed, upsert=True)

    def save_strategy(self, strategy):
        id, packed = self._serialize(strategy)
        self.strategies.update({'_id': id}, packed, upsert=True)

    def save_account_event(self, account_event):
        raise NotImplementedError()

    def save_order_event(self, order_event):
        raise NotImplementedError()

    def save_execution_event(self, execution_event):
        raise NotImplementedError()
