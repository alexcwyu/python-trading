import abc

from algotrader import HasId
from algotrader.provider import Provider
from algotrader.utils.ser_deser import Serializable


class DataStore(Provider):
    Cassandra = "Cassandra"
    KDB = "KDB"
    Influx = "Influx"
    Mongo = "Mongo"

    __metaclass__ = abc.ABCMeta

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


class Persistable(Serializable):
    __metaclass__ = abc.ABCMeta

    def save(self, data_store):
        pass

    def load(self):
        pass
