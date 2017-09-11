# https://github.com/veox/python3-krakenex
# pip install krakenex
# https://www.reddit.com/r/kraken_traders/comments/6f6e9h/krakenapi_delivering_inconsistent_false_ohlc_data/
# https://github.com/veox/python3-krakenex/tree/master/examples


# import decimal
# import time
# 

# 
# pair = 'XETHZEUR'
# # NOTE: for the (default) 1-minute granularity, the API seems to provide
# # data up to 12 hours old only!
# since = str(1499000000)  # UTC 2017-07-02 12:53:20
# 
# k = krakenex.API()
# 
# 
# def now():
#     return decimal.Decimal(time.time())
# 
# 
# def lineprint(msg, targetlen=72):
#     line = '-' * 5 + ' '
#     line += str(msg)
# 
#     l = len(line)
#     if l < targetlen:
#         trail = ' ' + '-' * (targetlen - l - 1)
#         line += trail
# 
#     print(line)
#     return
# 
# 
# while True:
#     lineprint(now())
# 
#     # comment out to reuse the same connection
#     # k.conn = krakenex.Connection()
# 
#     before = now()
#     ret = k.query_public('OHLC', req={'pair': pair, 'since': since})
#     after = now()
# 
#     # comment out to reuse the same connection
#     # k.conn.close()
# 
#     # comment out to track the same "since"
#     # since = ret['result']['last']
# 
#     # TODO: don't repeat-print if list too short
#     bars = ret['result'][pair]
#     for b in bars[:5]: print(b)
#     print('...')
#     for b in bars[-5:]: print(b)
# 
#     lineprint(after - before)
# 
#     time.sleep(20)

import krakenex

from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed


class KrakenBroker(Broker, Feed):
    def _start(self, app_context=None):
        self._api = krakenex.API()
        self._api.conn = krakenex.Connection()

    def _stop(self):
        self._api.close()

    def _get_server_time(self):
        return self._api.query_public("Time")

    def _get_asset_info(self, info=None, aclass=None, asset=None):
        return self._api.query_public("Assets", req={'info': info, 'aclass': aclass, 'asset': asset})

    def _get_tradable_asset_pairs(self, info=None, pair=None):
        return self._api.query_public("AssetPairs", req={'info': info, 'pair': pair})

    def _get_ticker_info(self, pair):
        return self._api.query_public("Ticker", req={'pair': pair})

    def _get_ohlc(self, pair, interval=1, since=None):
        return self._api.query_public("OHLC", req={'pair': pair, 'interval': interval, 'since': since})

    def _get_order_book(self, pair, count=None):
        return self._api.query_public("Depth", req={'pair': pair, 'count': count})

    def _get_trades(self, pair, since=None):
        return self._api.query_public("Trades", req={'pair': pair, 'since': since})

    def _get_spread(self, pair, since=None):
        return self._api.query_public("Spread", req={'pair': pair, 'since': since})

    def _get_trade_balance(self, aclass=None, asset="ZUSD"):
        return self._api.query_private("TradeBalance", req={'aclass': aclass, 'asset': asset})

    def _get_open_orders(self, trades=False, userref=None):
        return self._api.query_private("OpenOrders", req={'trades': trades, 'userref': userref})

    def _get_close_orders(self, trades=False, userref=None, start=None, end=None, closetime="both", ofs=None):
        return self._api.query_private("ClosedOrders",
                                       req={'trades': trades, 'userref': userref, "start": start, "end": end,
                                            "ofs": ofs, "closetime": closetime})

    def _query_orders(self, txid, trades=False, userref=None):
        return self._api.query_private("QueryOrders", req={'txid': txid, 'trades': trades, 'userref': userref})

    def _get_trade_history(self, type=None, trades=False, start=None, end=None, ofs=None):
        return self._api.query_private("TradesHistory",
                                       req={'ofs': ofs, 'type': type, 'trades': trades, 'start': start, 'end': end})

    def _query_trades(self, txid, trades=False):
        return self._api.query_private("QueryTrades", req={'txid': txid, 'trades': trades})

    def _query_open_positions(self, txid, docalcs=False):
        return self._api.query_private("OpenPositions", req={'txid': txid, 'docalcs': docalcs})

    def _get_ledgers_info(self, aclass=None, asset=None, type=None, start=None, end=None, ofs=None):
        return self._api.query_private("Ledgers",
                                       req={'aclass': aclass, 'asset': asset, 'type': type, 'start': start, 'end': end,
                                            'ofs': ofs})

    def _query_ledgers(self, id):
        return self._api.query_private("QueryLedgers", req={'id': id})

    def _get_trade_volume(self, pair=None, fee_info=None):
        return self._api.query_private("TradeVolume", req={'pair': pair, 'fee_info': fee_info})

    def _add_order(self, pair, type, ordertype, volume, price=None, price2=None, leverage=None, oflags=None, starttm=0,
                   expiretm=0, userref=None, validate=None):
        return self._api.query_private("AddOrder",
                                       req={'pair': pair, 'type': type, 'ordertype': ordertype, 'volume': volume,
                                            'price': price, 'price2': price2,
                                            'leverage': leverage, 'oflags': oflags, 'starttm': starttm,
                                            'expiretm': expiretm, 'userref': userref, 'validate': validate})

    def _cancel_order(self, txid):
        return self._api.query_private("CancelOrder", req={'txid': txid})

import time

broker = KrakenBroker()
broker.start()

since = str(1499000000)
pair = 'XETHZEUR'
while True:
    ret = broker._get_ohlc(pair=pair, since=since)
    since = ret['result']['last']
    bars = ret['result'][pair]

    for b in bars:
        print(b)
    print('...')
    time.sleep(20)