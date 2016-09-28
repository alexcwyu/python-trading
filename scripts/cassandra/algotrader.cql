// table to store historical stock quote data

CREATE KEYSPACE IF NOT EXISTS algotrader WITH replication ={'class':'SimpleStrategy','replication_factor':1};

USE algotrader;

// timeseries data
CREATE TABLE IF NOT EXISTS bars (
  inst_id varchar,
  type int,
  size int,
  begin_time bigint,
  timestamp bigint,
  open double,
  high double,
  low double,
  close double,
  vol bigint,
  adj_close double,
  PRIMARY KEY ((inst_id, type, size), timestamp)
);

CREATE TABLE IF NOT EXISTS quotes(
  inst_id varchar,
  timestamp bigint,
  bid double,
  ask double,
  bid_size int,
  ask_size int,
  PRIMARY KEY (inst_id, timestamp)
);

CREATE TABLE IF NOT EXISTS trades(
  inst_id varchar,
  timestamp bigint,
  price double,
  size int,
  PRIMARY KEY (inst_id, timestamp)
);

CREATE TABLE IF NOT EXISTS market_depths(
  inst_id varchar,
  provider_id int,
  timestamp bigint,
  position bigint,
  operation int,
  side int,
  price double,
  size int,
  PRIMARY KEY ((inst_id, provider_id), timestamp)
);

CREATE TABLE IF NOT EXISTS time_series(
  id varchar,
  data blob,
  PRIMARY KEY (id) // primary key
);

CREATE TABLE IF NOT EXISTS time_series_entry(
  id varchar,
  keys set<varchar>,
  desc varchar
  PRIMARY KEY (id) // primary key
);

CREATE TABLE IF NOT EXISTS time_series_data(
  id varchar,
  timestamp bigint,
  values map
  PRIMARY KEY (id, timestamp)
);

// ref data
CREATE TABLE IF NOT EXISTS instruments(
  inst_id varchar,
  name varchar,
  type varchar,
  symbol varchar,
  exch_id varchar,
  ccy_id varchar,
  alt_symbol map<varchar, varchar>,
  alt_exch_id map<varchar, varchar>,
  sector varchar,
  group varchar,
  und_inst_id varchar,
  expiry_date timestamp,
  factor double,
  strike double,
  put_call varchar,
  margin double,
  PRIMARY KEY (inst_id)
);

CREATE TABLE IF NOT EXISTS exchanges(
  exch_id varchar,
  name varchar,
  PRIMARY KEY (exch_id)
);

CREATE TABLE IF NOT EXISTS currencies(
  ccy_id varchar,
  name varchar,
  PRIMARY KEY (ccy_id)
);

// trade data
CREATE TABLE IF NOT EXISTS accounts(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS portfolios(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS orders(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS configs(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS strategies(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS account_updates(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS portfolio_updates(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS new_order_reqs(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS ord_cancel_reqs(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS ord_replace_reqs(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS exec_reports(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS ord_status_upds(
  id varchar,
  data blob,
  PRIMARY KEY (id)
);

// seq data
CREATE TABLE IF NOT EXISTS sequence(
  id varchar,
  seq counter,
  PRIMARY KEY (id)
);

