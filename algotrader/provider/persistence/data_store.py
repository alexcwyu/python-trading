import abc

from algotrader.provider import Provider
from algotrader.provider.feed import Feed
from algotrader.provider.subscription import QuoteSubscriptionType, MarketDepthSubscriptionType, BarSubscriptionType, \
    TradeSubscriptionType


class DataStore(Provider):
    Cassandra = "Cassandra"
    KDB = "KDB"
    Influx = "Influx"
    Mongo = "Mongo"
    InMemoryDB = "InMemoryDB"

    __metaclass__ = abc.ABCMeta

    def save(self, persistable):
        persistable.save(self)

    @abc.abstractmethod
    def load_all(self, clazz):
        raise NotImplementedError()

    def create_database(self):
        pass

    def remove_database(self):
        pass


class RefDataStore(DataStore):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_instrument(self, instrument):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_exchange(self, exchange):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_currency(self, currency):
        raise NotImplementedError()


class TimeSeriesDataStore(DataStore, Feed):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_bar(self, bar):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_quote(self, quote):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_trade(self, trade):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_market_depth(self, market_depth):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_time_series(self, timeseries):
        raise NotImplementedError()

    def unsubscribe_mktdata(self, *sub_keys):
        pass

    def subscribe_mktdata(self, *sub_keys):
        self.load_and_publish_mktdata(*sub_keys)

    def load_and_publish_mktdata(self, *sub_keys):
        data_event_bus = self.app_context.event_bus.data_subject
        data_list = self.load_mktdata(*sub_keys)
        sorted_data_list = sorted(data_list, key=lambda data: data.timestamp)
        for data in sorted_data_list:
            data_event_bus.on_next(data)

    def load_mktdata(self, *sub_keys):
        data_list = []
        for sub_key in sub_keys:
            if isinstance(sub_key.subscription_type, QuoteSubscriptionType):
                data_list.extend(self.load_bars(sub_key))
            elif isinstance(sub_key.subscription_type, MarketDepthSubscriptionType):
                data_list.extend(self.load_bars(sub_key))
            elif isinstance(sub_key.subscription_type, BarSubscriptionType):
                data_list.extend(self.load_bars(sub_key))
            elif isinstance(sub_key.subscription_type, TradeSubscriptionType):
                data_list.extend(self.load_bars(sub_key))
        return data_list

    @abc.abstractmethod
    def load_bars(self, sub_key):
        raise NotImplementedError()

    @abc.abstractmethod
    def load_quotes(self, sub_key):
        raise NotImplementedError()

    @abc.abstractmethod
    def load_trades(self, sub_key):
        raise NotImplementedError()

    @abc.abstractmethod
    def load_market_depths(self, sub_key):
        raise NotImplementedError()


class TradeDataStore(DataStore):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_account(self, account):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_portfolio(self, portfolio):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_order(self, order):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_strategy(self, strategy):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_config(self, config):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_account_update(self, account_update):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_portfolio_update(self, portfolio_update):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_new_order_req(self, new_order_req):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_ord_cancel_req(self, ord_cancel_req):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_ord_replace_req(self, ord_replace_req):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_exec_report(self, exec_report):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_ord_status_upd(self, ord_status_upd):
        raise NotImplementedError()


class SequenceDataStore(DataStore):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_sequence(self, key, seq):
        raise NotImplementedError()
