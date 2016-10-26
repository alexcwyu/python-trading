CREATE TABLE IF NOT EXISTS bars (
  inst_id int,
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
  inst_id int,
  timestamp bigint,
  bid double,
  ask double,
  bid_size int,
  ask_size int,
  PRIMARY KEY (inst_id, timestamp)
);

CREATE TABLE IF NOT EXISTS trades(
  inst_id int,
  timestamp bigint,
  price double,
  size int,
  PRIMARY KEY (inst_id, timestamp)
);

CREATE TABLE IF NOT EXISTS market_depths(
  inst_id int,
  provider_id varchar,
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
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS instruments(
  inst_id int,
  name varchar,
  type varchar,
  symbol varchar,
  exch_id varchar,
  ccy_id varchar,
  alt_symbol map<varchar, varchar>,
  alt_exch_id map<varchar, varchar>,
  sector varchar,
  group varchar,
  und_inst_id int,
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
CREATE TABLE IF NOT EXISTS sequences(
  id varchar,
  seq bigint,
  PRIMARY KEY (id)
);

