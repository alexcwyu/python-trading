// table to store historical stock quote data

CREATE KEYSPACE IF NOT EXISTS marketdata WITH replication ={'class':'SimpleStrategy','replication_factor':1};

USE marketdata;

CREATE TABLE IF NOT EXISTS bar (
  inst_id varchar, // stock symbol
  type int, //bar type
  size int, //bar size
  timestamp timestamp, // timestamp of bar
  open double, // open price
  high double, // high price
  low double, // low price
  close double, // close price
  vol bigint, // volume
  adj_close double, // close price
  openint bigint, // openInt
  PRIMARY KEY (inst_id, type, size, timestamp) // primary key
);


CREATE TABLE IF NOT EXISTS quote(
  inst_id int, // stock symbol
  timestamp timestamp, // timestamp of quote
  bid double, // bid
  ask double, // ask
  bid_size int, // bid size
  ask_size int, // ask size
  PRIMARY KEY (inst_id, timestamp) // primary key
);

CREATE TABLE IF NOT EXISTS trade(
  inst_id int, // stock symbol
  timestamp timestamp, // timestamp of trade
  price double, // price
  size int, // size
  PRIMARY KEY (inst_id, timestamp) // primary key
);

CREATE TABLE IF NOT EXISTS market_depth(
  inst_id int, // stock symbol
  provider_id int, // provider
  timestamp timestamp, // timestamp
  position bigint,
  operation int,
  side int,
  price double,
  size int,
  PRIMARY KEY (inst_id, provider_id, timestamp) // primary key
);