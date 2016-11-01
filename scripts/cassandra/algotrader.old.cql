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
  industry varchar,
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
  portf_id varchar,
  data blob,
  PRIMARY KEY (portf_id)
);


CREATE TABLE IF NOT EXISTS orders(
  cl_id varchar,
  cl_ord_id bigint,
  timestamp bigint,

  portf_id varchar,
  broker_id varchar,
  broker_ord_id varchar,

  inst_id varchar,
  action int,

  type int,
  qty double,
  limit_price double,
  stop_price double,
  tif int,
  oca_tag varchar,
  params map,

  status int,
  filled_qty double,
  avg_price double,
  last_qty double,
  last_price double,
  stop_limit_ready boolean,
  trailing_stop_exec_price double,

  PRIMARY KEY (cl_id, cl_ord_id)
);


CREATE TABLE IF NOT EXISTS configs(
  config_id varchar,
  data blob,
  PRIMARY KEY (config_id)
);

CREATE TABLE IF NOT EXISTS strategies(
  stg_id varchar,
  data blob,
  PRIMARY KEY (stg_id)
);

CREATE TABLE IF NOT EXISTS account_updates(
  timestamp bigint,
  id bigint,
  account_name varchar,

  key varchar,
  ccy varchar,
  val double,

  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS portfolio_updates(
  timestamp bigint,
  id bigint,

  inst_id varchar,
  position double,
  mkt_price double,
  mkt_value double,
  avg_cost double,
  unrealized_pnl double,
  realized_pnl double,
  account_name varchar,

  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS new_order_reqs(
  cl_id varchar,
  cl_ord_id bigint,
  timestamp bigint,

  portf_id varchar,
  broker_id varchar,
  inst_id varchar,
  action int,

  type int,
  qty double,
  limit_price double,
  stop_price double
  tif int,
  oca_tag varchar,
  params map,


  PRIMARY KEY (cl_id, cl_ord_id)
);


CREATE TABLE IF NOT EXISTS ord_cancel_reqs(
  cl_id varchar,
  cl_ord_id bigint,
  timestamp bigint,

  params map,
  PRIMARY KEY (cl_id, cl_ord_id)
);


CREATE TABLE IF NOT EXISTS ord_replace_reqs(
  cl_id varchar,
  cl_ord_id bigint,
  timestamp bigint,

  type int,
  qty double,
  limit_price double,
  stop_price double
  tif int,
  oca_tag varchar,
  params map,

  PRIMARY KEY (cl_id, cl_ord_id)
);


CREATE TABLE IF NOT EXISTS exec_reports(
  broker_id varchar,
  ord_id varchar,
  cl_id varchar,
  cl_ord_id bigint,
  inst_id varchar,
  timestamp bigint,

  er_id varchar,
  last_qty double,
  last_price double,
  commission double,
  filled_qty double,
  avg_price double,
  status varchar,

  PRIMARY KEY (er_id)
);


CREATE TABLE IF NOT EXISTS ord_status_upds(
  broker_id varchar,
  ord_id varchar,
  cl_id varchar,
  cl_ord_id bigint,
  inst_id varchar,
  timestamp bigint,

  ord_status_id varchar,
  filled_qty double,
  avg_price double,
  status varchar,

  PRIMARY KEY (ord_status_id)
);

// seq data
CREATE TABLE IF NOT EXISTS sequence(
  id varchar,
  seq counter
  PRIMARY KEY (id)
);

