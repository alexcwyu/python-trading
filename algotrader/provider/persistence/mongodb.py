from pymongo import MongoClient

from algotrader.config.persistence import MongoDBConfig
from algotrader.provider.persistence.data_store import DataStore, RefDataStore, TimeSeriesDataStore, TradeDataStore, \
    SequenceDataStore
from algotrader.utils import logger
from algotrader.utils.date_utils import DateUtils
from algotrader.utils.ser_deser import MapSerializer


class MongoDBDataStore(RefDataStore, TradeDataStore, TimeSeriesDataStore, SequenceDataStore):
    def __init__(self):
        super(MongoDBDataStore, self).__init__()

    def _start(self, app_context, **kwargs):
        self.mongo_config = app_context.app_config.get_config(MongoDBConfig)
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
        self.configs = self.db['configs']

        self.account_updates = self.db['account_updates']
        self.portfolio_updates = self.db['portfolio_updates']

        self.new_order_reqs = self.db['new_order_reqs']
        self.ord_cancel_reqs = self.db['ord_cancel_reqs']
        self.ord_replace_reqs = self.db['ord_replace_reqs']

        self.exec_reports = self.db['exec_reports']
        self.ord_status_upds = self.db['ord_status_upds']

        self.sequences = self.db['sequences']
        self.serializer = MapSerializer

    def _stop(self):
        if self.client:
            if self.mongo_config.delete_at_stop:
                self.remove_database()
            self.client.close()

    def remove_database(self):
        try:
            self.client.drop_database(self.mongo_config.dbname)
        except:
            pass

    def id(self):
        return DataStore.Mongo

    def load_all(self, clazz):
        if clazz == 'sequences':
            return {data['_id']: data['seq'] for data in self.db[clazz].find()}

        result = []
        for data in self.db[clazz].find():
            obj = self.serializer.deserialize(data)
            # obj = clazz()
            # obj.deserialize(result)
            result.append(obj)
        return result

    def _serialize(self, serializable):
        # return serializable.id(), serializable.serialize()
        return serializable.id(), self.serializer.serialize(serializable)

    # RefDataStore
    def save_instrument(self, instrument):
        logger.info("[%s] saving %s" % (self.__class__.__name__, instrument))
        id, packed = self._serialize(instrument)
        self.instruments.update({'_id': id}, packed, upsert=True)

    def save_exchange(self, exchange):
        logger.info("[%s] saving %s" % (self.__class__.__name__, exchange))
        id, packed = self._serialize(exchange)
        self.exchanges.update({'_id': id}, packed, upsert=True)

    def save_currency(self, currency):
        logger.info("[%s] saving %s" % (self.__class__.__name__, currency))
        id, packed = self._serialize(currency)
        self.currencies.update({'_id': id}, packed, upsert=True)

    # TimeSeriesDataStore
    def save_bar(self, bar):
        logger.info("[%s] saving %s" % (self.__class__.__name__, bar))
        id, packed = self._serialize(bar)
        self.bars.update({'_id': id}, packed, upsert=True)

    def save_quote(self, quote):
        logger.info("[%s] saving %s" % (self.__class__.__name__, quote))
        id, packed = self._serialize(quote)
        self.quotes.update({'_id': id}, packed, upsert=True)

    def save_trade(self, trade):
        logger.info("[%s] saving %s" % (self.__class__.__name__, trade))
        id, packed = self._serialize(trade)
        self.trades.update({'_id': id}, packed, upsert=True)

    def save_market_depth(self, market_depth):
        id, packed = self._serialize(market_depth)
        self.market_depths.update({'_id': id}, packed, upsert=True)

    def save_time_series(self, timeseries):
        logger.info("[%s] saving %s" % (self.__class__.__name__, timeseries))
        id, packed = self._serialize(timeseries)
        self.time_series.update({'_id': id}, packed, upsert=True)

    def load_bars(self, sub_key):
        from_timestamp = DateUtils.date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = DateUtils.date_to_unixtimemillis(sub_key.to_date)
        return [self.serializer.deserialize(data)
                for data in self.bars.find({"__slots__.inst_id": sub_key.inst_id,
                                            "__slots__.type": sub_key.subscription_type.bar_type,
                                            "__slots__.size": sub_key.subscription_type.bar_size,
                                            "__slots__.timestamp": {"$gte": from_timestamp,
                                                          "$lt": to_timestamp}
                                            })]

    def load_quotes(self, sub_key):
        from_timestamp = DateUtils.date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = DateUtils.date_to_unixtimemillis(sub_key.to_date)
        return [self.serializer.deserialize(data)
                for data in self.quotes.find({"__slots__.inst_id": sub_key.inst_id,
                                              "__slots__.timestamp": {"$gte": from_timestamp,
                                                            "$lt": to_timestamp}
                                              })]

    def load_trades(self, sub_key):
        from_timestamp = DateUtils.date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = DateUtils.date_to_unixtimemillis(sub_key.to_date)
        return [self.serializer.deserialize(data)
                for data in self.trades.find({"__slots__.inst_id": sub_key.inst_id,
                                              "__slots__.timestamp": {"$gte": from_timestamp,
                                                            "$lt": to_timestamp}
                                              })]

    def load_market_depths(self, sub_key):
        from_timestamp = DateUtils.date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = DateUtils.date_to_unixtimemillis(sub_key.to_date)
        return [self.serializer.deserialize(data)
                for data in self.market_depths.find({"__slots__.inst_id": sub_key.inst_id,
                                                     "__slots__.timestamp": {
                                                         "$gte": from_timestamp,
                                                         "$lt": to_timestamp}
                                                     })]

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

    def save_config(self, config):
        id, packed = self._serialize(config)
        self.configs.update({'_id': id}, packed, upsert=True)

    def save_account_update(self, account_update):
        id, packed = self._serialize(account_update)
        self.account_updates.update({'_id': id}, packed, upsert=True)

    def save_portfolio_update(self, portfolio_update):
        id, packed = self._serialize(portfolio_update)
        self.portfolio_updates.update({'_id': id}, packed, upsert=True)

    def save_new_order_req(self, new_order_req):
        id, packed = self._serialize(new_order_req)
        self.new_order_reqs.update({'_id': id}, packed, upsert=True)

    def save_ord_cancel_req(self, ord_cancel_req):
        id, packed = self._serialize(ord_cancel_req)
        self.ord_cancel_reqs.update({'_id': id}, packed, upsert=True)

    def save_ord_replace_req(self, ord_replace_req):
        id, packed = self._serialize(ord_replace_req)
        self.ord_replace_reqs.update({'_id': id}, packed, upsert=True)

    def save_exec_report(self, exec_report):
        id, packed = self._serialize(exec_report)
        self.exec_reports.update({'_id': id}, packed, upsert=True)

    def save_ord_status_upd(self, ord_status_upd):
        id, packed = self._serialize(ord_status_upd)
        self.ord_status_upds.update({'_id': id}, packed, upsert=True)

    # SequenceDataStore
    def save_sequence(self, key, seq):
        self.sequences.update({'_id': key}, {'seq': seq}, upsert=True)
