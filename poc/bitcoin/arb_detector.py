
import ccxt
import asyncio

class MarketData:
    def __init__(self, exch_id, symbol):
        self.exch_id = exch_id
        self.symbol = symbol

        self.current_bid = None
        self.current_ask = None
        self.current_bid_size = None
        self.current_ask_size = None
        self.current_spread = None
        self.current_bids = []
        self.current_asks = []

        self.high = None
        self.low = None
        self.last = None

        self.orderbooks= []
        self.tickers= []


    def update_orderbook(self, orderbook):
        if len(orderbook['bids']) > 0:
            self.current_bid = bid = orderbook['bids'][0][0]
            self.current_bid_size = bid = orderbook['bids'][0][1]
        else:
            self.current_bid = None
            self.current_bid_size = None

        if len(orderbook['asks']) > 0:
            self.current_ask = bid = orderbook['asks'][0][0]
            self.current_ask_size = bid = orderbook['asks'][0][1]
        else:
            self.current_ask = None
            self.current_ask_size = None

        self.current_spread = (self.current_ask - self.current_bid) if (self.current_bid and self.current_ask) else None
        self.current_bids = orderbook['bids']
        self.current_asks = orderbook['asks']

        self.orderbooks.append(orderbook)

    def update_ticker(self, ticker):

        self.high = ticker['high']
        self.low = ticker['low']
        self.last = ticker['last']

        self.tickers.append(ticker)


inst_id_map = {}
inst_symbol_map = {}
base_quote_symbol_map = {}
quote_base_symbol_map = {}
symbol_exch_map = {}


exchanges_map = {}
market_data_map = {}

#exchanges = {exch: getattr(ccxt, exch)() for exch in ccxt.exchanges}

symbols = ['BTC/USD']

#exch_ids = ccxt.exchanges
exch_ids = [
    'anxpro',
    'binance',
    'bitmex',
    'bitstamp',
    'bittrex',
    'ccex',
    'cex',
    'gatecoin',
    'gdax',
    'gemini']

for exch_id in exch_ids:
    try:

        print("creating ", exch_id)
        exch= getattr(ccxt, exch_id)()
        exchanges_map[exch_id] = exch

        for inst in exch.load_markets().values():
            inst_id_map[inst['id']] = inst
            inst_symbol_map[inst['symbol']] = inst
            if not inst['symbol'] in symbol_exch_map:
                symbol_exch_map[inst['symbol']] = set()
            symbol_exch_map[inst['symbol']].add(exch_id)

            if not inst['symbol'] in market_data_map:
                market_data_map[inst['symbol']] = {}
            market_data_map[inst['symbol']][exch_id] = MarketData(exch_id=exch_id, symbol=inst['symbol'])

            if not inst['base'] in base_quote_symbol_map:
                base_quote_symbol_map[inst['base']] = {}
            base_quote_symbol_map[inst['base']][inst['quote']] = inst

            if not inst['quote'] in quote_base_symbol_map:
                quote_base_symbol_map[inst['quote']] = {}
            quote_base_symbol_map[inst['quote']][inst['base']] = inst

        print("createed exchange ", exch_id)
    except Exception as e:
        print("failed to create exchange ", exch_id, e)


import threading

import time

def fetch_symbol_from_exchange(exch_id, symbol):
    while True:
        try:
            #print('downloading {} from exchange {}'.format(symbol, exch_id))
            market_data = market_data_map[symbol][exch_id]
            exch = exchanges_map[exch_id]
            market_data.update_orderbook(exch.fetch_order_book(symbol))
            market_data.update_ticker(exch.fetchTicker(symbol))
            #print('downloaded {} from exchange {}'.format(symbol, exch_id))
            time.sleep(2)
        except Exception as e:
            pass
            #print('failed to download {} from exchange {}'.format(symbol, exch_id))


def detect_arb(symbol, loop = False):
    while True:
        try:
            time.sleep(2)
            print ("\n\n###### {} ".format(symbol))

            market_datas = market_data_map[symbol]
            highest_bids =sorted([(market_data.current_bid, market_data) for market_data in market_datas.values() if market_data.current_bid], reverse=True)
            lowest_asks = sorted([(market_data.current_ask, market_data) for market_data in market_datas.values() if market_data.current_ask])
            highest_asks = sorted(lowest_asks, reverse=True)

            print ("ASK {} ".format(symbol))
            for ask in highest_asks:
                print('{:>12}  {:10.4f}  {:14.4f}'.format(ask[1].exch_id, ask[0], ask[1].current_ask_size))

            print ("BID {} ".format(symbol))
            for bid in highest_bids:
                print('{:>12}  {:10.4f}  {:14.4f}'.format(bid[1].exch_id, bid[0], bid[1].current_bid_size))
            #
            # print ("Pair {} ".format(symbol))
            # for i in range(len(market_datas)):
            #     if highest_bids[i][0] > lowest_asks[i][0]:
            #         print('{:>12}  {:6.4f}  {:6.4f}  {:>12}'.format(highest_bids[i][1].exch_id, highest_bids[i][0], lowest_asks[i][0], lowest_asks[i][1].exch_id))

            if not loop:
                break
        except Exception as e:
            print('failed to ardetect_arb {}'.format(symbol))



# fetch_tasks = [fetch_symbol_from_exchange(exch_id, symbol) for symbol in symbols for exch_id in symbol_exch_map[symbol]]
# arb_tasks = [detect_arb(symbol) for symbol in symbols]
#
# tasks = fetch_tasks + arb_tasks
# loop = asyncio.get_event_loop()
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()



threads = []
for symbol in symbols :
    for exch_id in symbol_exch_map[symbol]:
        t = threading.Thread(target=fetch_symbol_from_exchange, args=(exch_id, symbol,))
        threads.append(t)
        t.start()

#
# while(True):
#     for symbol in symbols:
#         detect_arb(symbol)


for symbol in symbols:
    t = threading.Thread(target=detect_arb, args=(symbol,True, ))
    threads.append(t)
    t.start()



for t in threads:
    t.join()