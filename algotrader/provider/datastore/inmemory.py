import _pickle as pickle

import os

from algotrader.provider.datastore import DataStore, SimpleDataStore
from algotrader.utils.date import date_to_unixtimemillis
from algotrader.utils.model import model_to_dict, get_model_from_db_name, dict_to_model, get_model_id
from algotrader.utils.ref_data import *
from algotrader import Context


class InMemoryDataStore(SimpleDataStore):
    def __init__(self):
        super(InMemoryDataStore, self).__init__()

    def _start(self, app_context: Context) -> None:
        self.file = self._get_datastore_config("file")
        self.create_at_start = app_context.config.get_app_config("createDBAtStart")
        self.delete_at_stop = app_context.config.get_app_config("deleteDBAtStop")

        try:
            self.db = pickle.load(open(self.file, "rb"))
        except:
            self.db = {}

        self.bars = self._get_data('bars')
        self.quotes = self._get_data('quotes')
        self.trades = self._get_data('trades')
        self.market_depths = self._get_data('market_depths')
        self.time_series = self._get_data('time_series')

        self.instruments = self._get_data('instruments')
        self.currencies = self._get_data('currencies')
        self.exchanges = self._get_data('exchanges')

        self.accounts = self._get_data('accounts')
        self.portfolios = self._get_data('portfolios')
        self.orders = self._get_data('orders')
        self.strategies = self._get_data('strategies')
        self.configs = self._get_data('configs')

        self.account_updates = self._get_data('account_updates')
        self.portfolio_updates = self._get_data('portfolio_updates')

        self.new_order_reqs = self._get_data('new_order_reqs')
        self.ord_cancel_reqs = self._get_data('ord_cancel_reqs')
        self.ord_replace_reqs = self._get_data('ord_replace_reqs')

        self.exec_reports = self._get_data('exec_reports')
        self.ord_status_upds = self._get_data('ord_status_upds')

        self.sequences = self._get_data('sequences')

        self.load_from_csv(
            self._get_datastore_config("instCSV"),
            self._get_datastore_config("ccyCSV"),
            self._get_datastore_config("exchCSV"))

    def _get_data(self, key):
        if key not in self.db:
            self.db[key] = {}
        return self.db[key]

    def _stop(self):
        if self.delete_at_stop:
            self.remove_database()
        else:
            pickle.dump(self.db, open(self.file, "wb+"))

    def remove_database(self):
        try:
            os.remove(self.file)
        except:
            pass

    def id(self):
        return DataStore.InMemory

    def load_all(self, db):
        result = []
        if db == 'sequences':
            return self.sequences
        clazz = get_model_from_db_name(db)
        for id, data in self.db.get(db, {}).items():
            obj = dict_to_model(clazz, data)
            result.append(obj)
        return result

    def load_from_csv(self, inst_csv, ccy_csv, exch_csv):
        load_inst_from_csv(self, inst_csv)
        load_ccy_from_csv(self, ccy_csv)
        load_exch_from_csv(self, exch_csv)

    def _serialize(self, serializable):
        return get_model_id(serializable), model_to_dict(serializable)

    # RefDataStore
    def save_instrument(self, instrument):
        id, packed = self._serialize(instrument)
        self.instruments[id] = packed

    def save_exchange(self, exchange):
        id, packed = self._serialize(exchange)
        self.exchanges[id] = packed

    def save_currency(self, currency):
        id, packed = self._serialize(currency)
        self.currencies[id] = packed

    # TimeSeriesDataStore
    def save_bar(self, bar):
        id, packed = self._serialize(bar)
        self.bars[id] = packed

    def save_quote(self, quote):
        id, packed = self._serialize(quote)
        self.quotes[id] = packed

    def save_trade(self, trade):
        id, packed = self._serialize(trade)
        self.trades[id] = packed

    def save_market_depth(self, market_depth):
        id, packed = self._serialize(market_depth)
        self.market_depths[id] = packed

    def save_time_series(self, timeseries):
        id, packed = self._serialize(timeseries)
        self.time_series[id] = packed

    def __matches_data(self, data, inst_id, from_timestamp, to_timestamp):
        return inst_id == data.inst_id and data.timestamp >= from_timestamp and data.timestamp < to_timestamp

    def load_bars(self, sub_key):
        from_timestamp = date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = date_to_unixtimemillis(sub_key.to_date)
        return [bar for bar in self.load_all('bars') if self.__matches_data(bar, sub_key.inst_id, from_timestamp,
                                                                            to_timestamp) and bar.type == sub_key.subscription_type.bar_type and bar.size == sub_key.subscription_type.bar_size]

    def load_quotes(self, sub_key):
        from_timestamp = date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = date_to_unixtimemillis(sub_key.to_date)
        return [quote for quote in self.load_all('quotes') if
                self.__matches_data(quote, sub_key.inst_id, from_timestamp, to_timestamp)]

    def load_trades(self, sub_key):
        from_timestamp = date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = date_to_unixtimemillis(sub_key.to_date)
        return [trade for trade in self.load_all('trades') if
                self.__matches_data(trade, sub_key.inst_id, from_timestamp, to_timestamp)]

    def load_market_depths(self, sub_key):
        from_timestamp = date_to_unixtimemillis(sub_key.from_date)
        to_timestamp = date_to_unixtimemillis(sub_key.to_date)
        return [market_depth for market_depth in self.load_all('market_depths') if
                self.__matches_data(market_depth, sub_key.inst_id, from_timestamp, to_timestamp)]

    # TradeDataStore
    def save_account(self, account):
        id, packed = self._serialize(account)
        self.accounts[id] = packed

    def save_portfolio(self, portfolio):
        id, packed = self._serialize(portfolio)
        self.portfolios[id] = packed

    def save_order(self, order):
        id, packed = self._serialize(order)
        self.orders[id] = packed

    def save_strategy(self, strategy):
        id, packed = self._serialize(strategy)
        self.strategies[id] = packed

    def save_config(self, config):
        id, packed = self._serialize(config)
        self.configs[id] = packed

    def save_account_update(self, account_update):
        id, packed = self._serialize(account_update)
        self.account_updates[id] = packed

    def save_portfolio_update(self, portfolio_update):
        id, packed = self._serialize(portfolio_update)
        self.portfolio_updates[id] = packed

    def save_new_order_req(self, new_order_req):
        id, packed = self._serialize(new_order_req)
        self.new_order_reqs[id] = packed

    def save_ord_cancel_req(self, ord_cancel_req):
        id, packed = self._serialize(ord_cancel_req)
        self.ord_cancel_reqs[id] = packed

    def save_ord_replace_req(self, ord_replace_req):
        id, packed = self._serialize(ord_replace_req)
        self.ord_replace_reqs[id] = packed

    def save_exec_report(self, exec_report):
        id, packed = self._serialize(exec_report)
        self.exec_reports[id] = packed

    def save_ord_status_upd(self, ord_status_upd):
        id, packed = self._serialize(ord_status_upd)
        self.ord_status_upds[id] = packed

    # SequenceDataStore
    def save_sequence(self, key, seq):
        self.sequences[key] = seq
