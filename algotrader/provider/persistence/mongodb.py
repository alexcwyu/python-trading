from pymongo import MongoClient

from algotrader.config.persistence import MongoDBConfig
from algotrader.model.model_helper import *
from algotrader.model.protobuf_to_dict import protobuf_to_dict, dict_to_protobuf
from algotrader.model.ref_data_pb2 import *
from algotrader.model.time_series_pb2 import *
from algotrader.model.trade_data_pb2 import *
from algotrader.utils import logger
from algotrader.utils.date_utils import DateUtils
from algotrader.utils.ser_deser import MapSerializer


class MongoDBDataStore(object):
    def __init__(self):
        super(MongoDBDataStore, self).__init__()

    def _start(self, app_context, **kwargs):
        self.mongo_config = app_context.app_config.get_config(MongoDBConfig)
        self.client = MongoClient(host=self.mongo_config.host, port=self.mongo_config.port)
        self.db = self.client[self.mongo_config.dbname]

        self.db_map = {
            Instrument: self.db['instruments'],
            Exchange: self.db['exchanges'],
            Currency: self.db['currencies'],
            Country: self.db['countries'],
            HolidaySeries: self.db['trading_holidays'],
            TradingHours: self.db['trading_hours'],
            TimeZone: self.db['timezones'],

            TimeSeries: self.db['time_series'],

            Bar: self.db['bars'],
            Trade: self.db['trades'],
            Quote: self.db['quotes'],
            MarketDepth: self.db['market_depths'],

            NewOrderRequest: self.db['new_order_requests'],
            OrderReplaceRequest: self.db['order_replace_requests'],
            OrderCancelRequest: self.db['order_cancel_requests'],

            OrderStatusUpdate: self.db['order_status_updates'],
            ExecutionReport: self.db['execution_reports'],
            AccountUpdate: self.db['account_updates'],
            PortfolioUpdate: self.db['portfolio_updates'],

            AccountState: self.db['account_states'],
            PortfolioState: self.db['portfolio_states'],
            StrategyState: self.db['strategy_states'],
            OrderState: self.db['order_states'],

            Config: self.db['configs']

        }

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
        return "Mongo"

    def _save(self, obj):
        logger.info("[%s] saving %s" % (self.__class__.__name__, obj))
        id = ModelHelper.get_id(obj)
        packed_data = protobuf_to_dict(obj)
        t = type(object)
        self.db_map[t].update({'_id': id}, packed_data, upsert=True)

    # RefDataStore
    def save_instrument(self, inst: Instrument):
        self._save(inst)

    def save_exchange(self, exchange: Exchange):
        self._save(exchange)

    def save_currency(self, currency: Currency):
        self._save(currency)

    def save_country(self, country: Country):
        self._save(country)

    def save_trading_holidays(self, trading_holidays: HolidaySeries):
        self._save(trading_holidays)

    def save_trading_hours(self, trading_hours: TradingHours):
        self._save(trading_hours)

    def save_timezone(self, timezone: TimeZone):
        self._save(timezone)

    # TimeSeriesDataStore
    def save_time_series(self, time_series: TimeSeries):
        self._save(time_series)

    def save_bar(self, bar: Bar):
        self._save(bar)

    def save_quote(self, quote: Quote):
        self._save(quote)

    def save_trade(self, trade: Trade):
        self._save(trade)

    def save_market_depth(self, market_depth: MarketDepth):
        self._save(market_depth)

    # TradeDataStore
    def save_new_order_requests(self, new_order_request: NewOrderRequest):
        self._save(new_order_request)

    def save_order_replace_requests(self, order_replace_request: OrderReplaceRequest):
        self._save(order_replace_request)

    def save_order_cancel_request(self, order_cancel_request: OrderCancelRequest):
        self._save(order_cancel_request)

    def save_execution_report(self, execution_report: ExecutionReport):
        self._save(execution_report)

    def save_order_status_update(self, order_status_update: OrderStatusUpdate):
        self._save(order_status_update)

    def save_account_update(self, account_update: AccountUpdate):
        self._save(account_update)

    def save_portfolio_update(self, portfolio_update: PortfolioUpdate):
        self._save(portfolio_update)

    def save_account_state(self, account_state: AccountState):
        self._save(account_state)

    def save_portfolio_state(self, portfolio_state: PortfolioState):
        self._save(portfolio_state)

    def save_strategy_state(self, strategy_state: StrategyState):
        self._save(strategy_state)

    def save_order_state(self, order_state: OrderState):
        self._save(order_state)

    def save_config(self, config):
        self._save(config)

    # SequenceDataStore
    def save_sequence(self, key, seq):
        self.sequences.update({'_id': key}, {'seq': seq}, upsert=True)

    def _deserialize(self, clazz, data):
        del data['_id']
        obj = dict_to_protobuf(clazz, data)
        return obj

    def load_all(self, clazz):
        if clazz == 'sequences':
            return {data['_id']: data['seq'] for data in self.db[clazz].find()}

        result = []
        for data in self.db_map[clazz].find():
            result.append(self._deserialize(clazz, data))
        return result

    def load_bars(self, sub_key):
        from_timestamp = DateUtils.date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = DateUtils.date_to_unixtimemillis(sub_key.to_date)
        return [self._deserialize(Bar, data)
                for data in self.bars.find(self._build_bar_query(sub_key))]

    def _build_bar_query(self, sub_key):
        from_timestamp = DateUtils.date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = DateUtils.date_to_unixtimemillis(sub_key.to_date)
        return {"__slots__.inst_id": sub_key.inst_id,
                "__slots__.type": sub_key.subscription_type.bar_type,
                "__slots__.size": sub_key.subscription_type.bar_size,
                "__slots__.timestamp": {"$gte": from_timestamp,
                                        "$lt": to_timestamp}
                }

    def _build_query(self, sub_key):
        from_timestamp = DateUtils.date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = DateUtils.date_to_unixtimemillis(sub_key.to_date)
        return {"__slots__.inst_id": sub_key.inst_id,
                "__slots__.timestamp": {"$gte": from_timestamp,
                                        "$lt": to_timestamp}
                }

    def load_quotes(self, sub_key):
        return [self._deserialize(Quote, data)
                for data in self.quotes.find(self._build_query(sub_key))]

    def load_trades(self, sub_key):
        return [self._deserialize(Trade, data)
                for data in self.trades.find(self._build_query(sub_key))]

    def load_market_depths(self, sub_key):
        return [self._deserialize(MarketDepth, data)
                for data in self.market_depths.find(self._build_query(sub_key))]
