#### DONE
- fill strategy & slippage & bar vol ratio & commission
- serialization
    json
    msgpack
- indicator / timeseries, reuse...

#### PIPELINE
- bar adj price
- strategy has it orderID  (clOrderID vs orderID)
- unify timeseries & dataseries, test performance
- support merge / append on dataSeries
- better API
	- market order, limit order
	- get position
	- get cash
	- above, below, crossAbove, crossBelow
	- refer API from ninjaTrader, MultiCharts, OpenQuant
- stats
	- pyfolio
	- sharpe
- clock / reminder / scheduler
- barFactory
	compress bar realtime
- subscription for marketData
- need onBarSlice??
- multi-time frame
	1hour, daily
- multi-session / multi-timezone
	data save as local timezone
	instrument linked exchange, which has default session and timezone
	instrument has it own session,. which can be overridden from the defaulted exchanged
- multi-strategy
	run 2 strategy together
- multi-portfolio
	2 strategies can share portfolio
- multi currency
	- portfolio support multi currency
- multi instrument
	strategy support multi-instrument, e.g. statsArb, bskTrade
- nested strategy
	master strategy manage sub-strategy
- reference data
	instrument
		session
		timezone
		currency
		exchange
		symbol_map <BrokerID, string>
		type
		subType
		sector / sub-sector / group / industry

	exchange
		session
		currency
		timezone
		holidayCurve
		country
	country
		currency
		holidayCurve
		timezone
	currency
	session
		trading session
	timezone


- more feed
	csv / pandas: google, yahoo, quandl
	kdb
	cassandra
	influx
- downloader
	historical
	realtime
- IB
	datafeed
	execution
- persistence
	mangoDB
- optimization
	- genetic algorithm
	- simulated annealing
- distributed / scheduled / batch
	- spark
	- multiprocess
- indicator
	- more native indicator
	- support TALIB
- display
	- read persisted result and display in html5 UI
	- search persisted result, sorted by criteria
- more strategy
	- openquant
	- quantopian
- GeneExpression / Decision Tree / Fuzzy Logic / C45 / Machine Learning