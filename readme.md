AlgoTrader
===========================

AlgoTrader is an **event driven algorithmic trading system**.

There is a python version and java version. They both share same API. 

The Java version is designed to support ultra low latency trading and FIX protocol.
It can process 10M+ event per seconds in a commodity pc hardware with I7 CPU.

The Python version support quick modelling / testing.  


Main Features (Python version)
------------------------------

 * Event driven.
 * Supports Market, Limit, Stop and StopLimit orders.
 * Supports CSV Feed (yahoo format)
 * Supports backtesting using Simulator, which supports differnet fill-strategy, slippage config, commission setting
 * Supports live-trading using Interactive Brokers
 * Technical indicators and filters like SMA, RSI, Bollinger Bands..
 * Performance metrics (use pyfolio)
 
 
TODO
----

 * persistance: Save the portfolio, account, result into DB and can load them back when system startup. 
 * Supports more CSV format, e.g. Google Finance, Quandl and NinjaTrader.
 * Supports more data feed e.g. Cassandra, InfluxDB, KDB 
 * Supports real time data persistance into various data store (e.g. CSV, Cassandra, Influx, KDB)
 * Aggregated TimeSeries (multiple Key - value)
 * Event profiler.
 * TA-Lib integration, support more TA indicator
 * HTML5 UI, to view the account, portfolio, control strategy and view performance (real time and historical performance)
 * Multiple currencies, timezone, and trading session.
 * Trading context, which include strategy config, data subscription info
 * Supports Machine Learning Library, e.g. Theano 
 * Supports Spark
 * Supports Parallel processing, for optimization and backtest. Results should be persisted into DB and can be viewed by HTML5 UI.