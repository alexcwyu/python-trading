import abc

from algotrader.provider.provider import Provider
from algotrader.utils.ser_deser import Serializable

class Query():
    __metaclass__ = abc.ABCMeta


class DataStore(Provider):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def query(self, query):
        raise NotImplementedError()

    def save(self, persistable):
        persistable.save(self)

    @abc.abstractmethod
    def load_all(self, clazz):
        raise NotImplementedError()


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


class TimeSeriesDataStore(DataStore):
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


class TradeDataStore(TimeSeriesDataStore):
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
    def save_account_event(self, account_event):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_order_event(self, order_event):
        raise NotImplementedError()

    @abc.abstractmethod
    def save_execution_event(self, execution_event):
        raise NotImplementedError()


class Persistable(Serializable):
    def save(self, data_store):
        pass

    def load(self):
        pass

    def id(self):
        return None