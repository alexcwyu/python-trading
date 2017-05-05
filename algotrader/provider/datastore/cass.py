# import os
#
# from cassandra.cluster import Cluster
#
# from algotrader.config.persistence import CassandraConfig
# from algotrader.event.market_data import Bar, Trade, Quote, MarketDepth
# from algotrader.provider.persistence import DataStore, SimpleDataStore
# from algotrader.trading.ref_data import Instrument, Currency, Exchange
# from algotrader.utils.logging import logger
# from algotrader.utils.ser_deser import MsgPackSerializer
#
#
# class CassandraDataStore(SimpleDataStore):
#     insert_bars_cql = """INSERT INTO bars (inst_id, type, size, begin_time, timestamp, open, high, low, close, vol, adj_close) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
#     insert_quotes_cql = """INSERT INTO quotes (inst_id, timestamp, bid, ask, bid_size, ask_size) VALUES (?, ?, ?, ?, ?, ?)"""
#     insert_trades_cql = """INSERT INTO trades (inst_id, timestamp, price, size) VALUES (?, ?, ?, ?)"""
#     insert_market_depths_cql = """INSERT INTO market_depths (inst_id, provider_id, timestamp, position, operation, side, price, size) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
#
#     insert_time_series_cql = """INSERT INTO time_series (id, data) VALUES (?, ?)"""
#
#     insert_instruments_cql = """INSERT INTO instruments (inst_id, name, type, symbol, exch_id, ccy_id, alt_symbols, alt_exch_id, sector, industry, und_inst_id, expiry_date, factor, strike, put_call, margin) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
#     insert_exchanges_cql = """INSERT INTO exchanges (exch_id, name) VALUES (?, ?)"""
#     insert_currencies_cql = """INSERT INTO currencies (ccy_id, name) VALUES (?, ?)"""
#
#     insert_accounts_cql = """INSERT INTO accounts (id, data) VALUES (?, ?)"""
#     insert_portfolios_cql = """INSERT INTO portfolios (id, data) VALUES (?, ?)"""
#     insert_orders_cql = """INSERT INTO orders (id, data) VALUES (?, ?)"""
#     insert_configs_cql = """INSERT INTO configs (id, data) VALUES (?, ?)"""
#     insert_strategies_cql = """INSERT INTO strategies (id, data) VALUES (?, ?)"""
#
#     insert_account_updates_cql = """INSERT INTO account_updates (id, data) VALUES (?, ?)"""
#     insert_portfolio_updates_cql = """INSERT INTO portfolio_updates (id, data) VALUES (?, ?)"""
#
#     insert_new_order_reqs_cql = """INSERT INTO new_order_reqs (id, data) VALUES (?, ?)"""
#     insert_ord_cancel_reqs_cql = """INSERT INTO ord_cancel_reqs (id, data) VALUES (?, ?)"""
#     insert_ord_replace_reqs_cql = """INSERT INTO ord_replace_reqs (id, data) VALUES (?, ?)"""
#
#     insert_exec_reports_cql = """INSERT INTO exec_reports (id, data) VALUES (?, ?)"""
#     insert_ord_status_upds_cql = """INSERT INTO ord_status_upds (id, data) VALUES (?, ?)"""
#
#     insert_sequences_cql = """INSERT INTO sequences (id, seq) VALUES (?, ?)"""
#
#     query_bars_cql = """SELECT inst_id, type, size, begin_time, timestamp, open, high, low, close, vol, adj_close FROM bars WHERE inst_id = ? AND type = ? AND size = ? AND timestamp >= ? AND timestamp < ?"""
#     query_quotes_cql = """SELECT inst_id, timestamp, bid, ask, bid_size, ask_size FROM quotes WHERE inst_id = ? AND timestamp >= ? AND timestamp < ?"""
#     query_trades_cql = """SELECT inst_id, timestamp, price, size FROM trades WHERE inst_id = ? AND timestamp >= ? AND timestamp < ?"""
#     query_market_depths_cql = """SELECT inst_id, provider_id, timestamp, position, operation, side, price, size FROM market_depths WHERE inst_id = ? AND provider_id = ? AND timestamp >= ? AND timestamp < ?"""
#
#     create_keyspace_cql = "CREATE KEYSPACE IF NOT EXISTS %s WITH replication ={'class':'SimpleStrategy','replication_factor':1};"
#     drop_keyspace_cql = "DROP KEYSPACE %s"
#
#     def __init__(self):
#         super(CassandraDataStore, self).__init__()
#
#     def _start(self, app_context):
#
#         self.cass_config = app_context.app_config.get_config(CassandraConfig)
#         self.cluster = Cluster(contact_points=self.cass_config.contact_points)
#
#         self.session = self.cluster.connect()
#
#         if self.cass_config.create_at_start:
#             self.create_database()
#         self.session.set_keyspace(self.cass_config.keyspace)
#
#         self.insert_bars_stmt = self.session.prepare(CassandraDataStore.insert_bars_cql)
#         self.insert_trades_stmt = self.session.prepare(CassandraDataStore.insert_trades_cql)
#         self.insert_quotes_stmt = self.session.prepare(CassandraDataStore.insert_quotes_cql)
#         self.insert_market_depths_stmt = self.session.prepare(CassandraDataStore.insert_market_depths_cql)
#
#         self.insert_time_series_stmt = self.session.prepare(CassandraDataStore.insert_time_series_cql)
#
#         self.insert_instruments_stmt = self.session.prepare(CassandraDataStore.insert_instruments_cql)
#         self.insert_exchanges_stmt = self.session.prepare(CassandraDataStore.insert_exchanges_cql)
#         self.insert_currencies_stmt = self.session.prepare(CassandraDataStore.insert_currencies_cql)
#
#         self.insert_accounts_stmt = self.session.prepare(CassandraDataStore.insert_accounts_cql)
#         self.insert_portfolios_stmt = self.session.prepare(CassandraDataStore.insert_portfolios_cql)
#         self.insert_orders_stmt = self.session.prepare(CassandraDataStore.insert_orders_cql)
#         self.insert_configs_stmt = self.session.prepare(CassandraDataStore.insert_configs_cql)
#         self.insert_strategies_stmt = self.session.prepare(CassandraDataStore.insert_strategies_cql)
#
#         self.insert_account_updates_stmt = self.session.prepare(CassandraDataStore.insert_account_updates_cql)
#         self.insert_portfolio_updates_stmt = self.session.prepare(CassandraDataStore.insert_portfolio_updates_cql)
#
#         self.insert_new_order_reqs_stmt = self.session.prepare(CassandraDataStore.insert_new_order_reqs_cql)
#         self.insert_ord_cancel_reqs_stmt = self.session.prepare(CassandraDataStore.insert_ord_cancel_reqs_cql)
#         self.insert_ord_replace_reqs_stmt = self.session.prepare(CassandraDataStore.insert_ord_replace_reqs_cql)
#
#         self.insert_exec_reports_stmt = self.session.prepare(CassandraDataStore.insert_exec_reports_cql)
#         self.insert_ord_status_upds_stmt = self.session.prepare(CassandraDataStore.insert_ord_status_upds_cql)
#
#         self.insert_sequences_stmt = self.session.prepare(CassandraDataStore.insert_sequences_cql)
#
#         self.query_bars_stmt = self.session.prepare(CassandraDataStore.query_bars_cql)
#         self.query_quotes_stmt = self.session.prepare(CassandraDataStore.query_quotes_cql)
#         self.query_trades_stmt = self.session.prepare(CassandraDataStore.query_trades_cql)
#         self.query_market_depths_stmt = self.session.prepare(CassandraDataStore.query_market_depths_cql)
#
#         self.serializer = MsgPackSerializer
#
#     def create_database(self):
#         logger.info("creating keyspace")
#         statement = CassandraDataStore.create_keyspace_cql % self.cass_config.keyspace
#         logger.info(statement)
#         self.session.execute(statement, timeout=30)
#         self.session.set_keyspace(self.cass_config.keyspace)
#
#         cql_path = os.path.abspath(os.path.join(os.path.dirname(__file__), self.cass_config.cql_script_path))
#         logger.info("creating table %s" % cql_path)
#         with open(cql_path) as cql_file:
#             for stmt in cql_file.read().split(";"):
#                 if len(stmt.strip()) > 0:
#                     logger.info(stmt)
#                     self.session.execute(stmt, timeout=30)
#         logger.info("table created")
#
#     def _stop(self):
#         if self.cass_config.delete_at_stop:
#             self.remove_database()
#         self.cluster.shutdown()
#
#     def remove_database(self):
#         logger.info("dropping keyspace")
#         self.session.execute(CassandraDataStore.drop_keyspace_cql % self.cass_config.keyspace)
#
#     def id(self):
#         return DataStore.Cassandra
#
#     def load_all(self, clazz):
#         result_list = self.session.execute("select * from %s " % clazz)
#
#         if clazz == 'sequences':
#             return {result.id: result.seq for result in result_list}
#         else:
#             results = []
#             for r in result_list:
#                 if clazz == 'bars':
#                     obj = Bar(inst_id=r.inst_id, type=r.type, size=r.size, begin_time=r.begin_time,
#                               timestamp=r.timestamp,
#                               open=r.open, high=r.high, low=r.low, close=r.close, vol=r.vol, adj_close=r.adj_close)
#                 elif clazz == 'trades':
#                     obj = Trade(inst_id=r.inst_id, timestamp=r.timestamp, price=r.price, size=r.size)
#                 elif clazz == 'quotes':
#                     obj = Quote(inst_id=r.inst_id, timestamp=r.timestamp, bid=r.bid, ask=r.ask, bid_size=r.bid_size,
#                                 ask_size=r.ask_size)
#                 elif clazz == 'market_depths':
#                     obj = MarketDepth(inst_id=r.inst_id, provider_id=r.provider_id, timestamp=r.timestamp,
#                                       position=r.position, operation=r.operation, side=r.side, price=r.price,
#                                       size=r.size)
#                 elif clazz == 'instruments':
#                     obj = Instrument(inst_id=r.inst_id, name=r.name, type=r.type, symbol=r.symbol, exch_id=r.exch_id,
#                                      ccy_id=r.ccy_id, alt_symbols=r.alt_symbols, alt_exch_id=r.alt_exch_id,
#                                      sector=r.sector,
#                                      industry=r.industry, und_inst_id=r.und_inst_id, expiry_date=r.expiry_date,
#                                      factor=r.factor,
#                                      strike=r.strike, put_call=r.put_call, margin=r.margin)
#                 elif clazz == 'currencies':
#                     obj = Currency(ccy_id=r.ccy_id, name=r.name)
#                 elif clazz == 'exchanges':
#                     obj = Exchange(exch_id=r.exch_id, name=r.name)
#                 else:
#                     obj = self.serializer.deserialize(r.data)
#                 results.append(obj)
#
#             return results
#
#     def _serialize(self, serializable):
#         return serializable.id(), self.serializer.serialize(serializable)
#
#     def _insert_blob_data(self, serializable, stmt):
#         id, packed = self._serialize(serializable)
#         bound_stmt = stmt.bind(["%s" % id, packed])
#         stmt = self.session.execute(bound_stmt)
#
#     # RefDataStore
#     def save_instrument(self, instrument):
#         bound_stmt = self.insert_instruments_stmt.bind([instrument.inst_id, instrument.name, instrument.type,
#                                                         instrument.symbol, instrument.exch_id, instrument.ccy_id,
#                                                         instrument.alt_symbols, instrument.alt_exch_id,
#                                                         instrument.sector,
#                                                         instrument.industry, instrument.und_inst_id,
#                                                         instrument.expiry_date,
#                                                         instrument.factor, instrument.strike, instrument.put_call,
#                                                         instrument.margin])
#         stmt = self.session.execute(bound_stmt)
#
#     def save_exchange(self, exchange):
#         bound_stmt = self.insert_exchanges_stmt.bind([exchange.exch_id, exchange.name])
#         stmt = self.session.execute(bound_stmt)
#
#     def save_currency(self, currency):
#         bound_stmt = self.insert_currencies_stmt.bind([currency.ccy_id, currency.name])
#         stmt = self.session.execute(bound_stmt)
#
#     # TimeSeriesDataStore
#     def save_bar(self, bar):
#         bound_stmt = self.insert_bars_stmt.bind([bar.inst_id, bar.type, bar.size, bar.begin_time, bar.timestamp,
#                                                  bar.open, bar.high, bar.low, bar.close, bar.vol, bar.adj_close])
#         stmt = self.session.execute(bound_stmt)
#
#     def save_quote(self, quote):
#         bound_stmt = self.insert_quotes_stmt.bind(
#             [quote.inst_id, quote.timestamp, quote.bid, quote.ask, quote.bid_size, quote.ask_size])
#         stmt = self.session.execute(bound_stmt)
#
#     def save_trade(self, trade):
#         bound_stmt = self.insert_trades_stmt.bind([trade.inst_id, trade.timestamp, trade.price, trade.size])
#         stmt = self.session.execute(bound_stmt)
#
#     def save_market_depth(self, market_depth):
#         bound_stmt = self.insert_market_depths_stmt.bind(
#             [market_depth.inst_id, market_depth.provider_id, market_depth.timestamp,
#              market_depth.position, market_depth.operation, market_depth.side, market_depth.price, market_depth.size])
#         stmt = self.session.execute(bound_stmt)
#
#     def save_time_series(self, timeseries):
#         self._insert_blob_data(timeseries, self.insert_time_series_stmt)
#
#     def load_bars(self, sub_key):
#         from_timestamp = date_to_unixtimemillis(sub_key.from_date)
#         to_timestamp = date_to_unixtimemillis(sub_key.to_date)
#
#         bound_stmt = self.query_bars_stmt.bind(
#             [sub_key.inst_id, sub_key.subscription_type.bar_type, sub_key.subscription_type.bar_size,
#              from_timestamp, to_timestamp])
#         result_list = self.session.execute(bound_stmt)
#
#         return [Bar(inst_id=r.inst_id, type=r.type, size=r.size, begin_time=r.begin_time, timestamp=r.timestamp,
#                     open=r.open, high=r.high, low=r.low, close=r.close, vol=r.vol, adj_close=r.adj_close) for r in
#                 result_list]
#
#     def load_quotes(self, sub_key):
#         from_timestamp = date_to_unixtimemillis(sub_key.from_date)
#         to_timestamp = date_to_unixtimemillis(sub_key.to_date)
#
#         bound_stmt = self.query_quotes_stmt.bind([sub_key.inst_id, from_timestamp, to_timestamp])
#         result_list = self.session.execute(bound_stmt)
#
#         return [Quote(inst_id=r.inst_id, timestamp=r.timestamp, bid=r.bid, ask=r.ask, bid_size=r.bid_size,
#                       ask_size=r.ask_size) for r in result_list]
#
#     def load_trades(self, sub_key):
#         from_timestamp = date_to_unixtimemillis(sub_key.from_date)
#         to_timestamp = date_to_unixtimemillis(sub_key.to_date)
#
#         bound_stmt = self.query_trades_stmt.bind([sub_key.inst_id, from_timestamp, to_timestamp])
#         result_list = self.session.execute(bound_stmt)
#         return [Trade(inst_id=r.inst_id, timestamp=r.timestamp, price=r.price, size=r.size) for r in result_list]
#
#     def load_market_depths(self, sub_key):
#         from_timestamp = date_to_unixtimemillis(sub_key.from_date)
#         to_timestamp = date_to_unixtimemillis(sub_key.to_date)
#
#         bound_stmt = self.query_market_depths_stmt.bind([sub_key.inst_id, sub_key.subscription_type.provider_id, from_timestamp, to_timestamp])
#         result_list = self.session.execute(bound_stmt)
#         return [MarketDepth(inst_id=r.inst_id, provider_id=r.provider_id, timestamp=r.timestamp,
#                             position=r.position, operation=r.operation, side=r.side, price=r.price, size=r.size) for r
#                 in result_list]
#
#     # TradeDataStore
#     def save_account(self, account):
#         self._insert_blob_data(account, self.insert_accounts_stmt)
#
#     def save_portfolio(self, portfolio):
#         self._insert_blob_data(portfolio, self.insert_portfolios_stmt)
#
#     def save_order(self, order):
#         self._insert_blob_data(order, self.insert_orders_stmt)
#
#     def save_strategy(self, strategy):
#         self._insert_blob_data(strategy, self.insert_strategies_stmt)
#
#     def save_config(self, config):
#         self._insert_blob_data(config, self.insert_configs_stmt)
#
#     def save_account_update(self, account_update):
#         self._insert_blob_data(account_update, self.insert_account_updates_stmt)
#
#     def save_portfolio_update(self, portfolio_update):
#         self._insert_blob_data(portfolio_update, self.insert_portfolio_updates_stmt)
#
#     def save_new_order_req(self, new_order_req):
#         self._insert_blob_data(new_order_req, self.insert_new_order_reqs_stmt)
#
#     def save_ord_cancel_req(self, ord_cancel_req):
#         self._insert_blob_data(ord_cancel_req, self.insert_ord_cancel_reqs_stmt)
#
#     def save_ord_replace_req(self, ord_replace_req):
#         self._insert_blob_data(ord_replace_req, self.insert_ord_replace_reqs_stmt)
#
#     def save_exec_report(self, exec_report):
#         self._insert_blob_data(exec_report, self.insert_exec_reports_stmt)
#
#     def save_ord_status_upd(self, ord_status_upd):
#         self._insert_blob_data(ord_status_upd, self.insert_ord_status_upds_stmt)
#
#     # SequenceDataStore
#     def save_sequence(self, key, seq):
#         bound_stmt = self.insert_sequences_stmt.bind([key, seq])
#         stmt = self.session.execute(bound_stmt)
