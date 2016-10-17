import csv
import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from algotrader.event.orderbook import OrderBook

from algotrader.event.market_data import Trade

directory = "/home/jason/workspace/data/Equity/SET/data20130717"
datfile = "TH0264010Z02.BK.20130717.dat"


def orderBookRowParser(row):
    ts = datetime.strptime(row[0], '%Y%m%d%H%M%S%f')
    raw_quote_row = row[1:]

    raw_bid_book = [x for x in raw_quote_row if x[0] == 'B']
    raw_ask_book = [x for x in raw_quote_row if x[0] == 'A']

    bid_split = [re.split('@', x) for x in raw_bid_book]
    bid_flattened = map(list, zip(*bid_split))
    bid_size = np.array([x[1:] for x in bid_flattened[0]], dtype='float')
    bid_array = np.array([x for x in bid_flattened[1]], dtype='float')

    ask_split = [re.split('@', x) for x in raw_ask_book]
    ask_flattened = map(list, zip(*ask_split))
    ask_size = np.array([x[1:] for x in ask_flattened[0]], dtype='float')
    ask_array = np.array([x for x in ask_flattened[1]], dtype='float')

    return OrderBook(instrument='Test', timestamp=ts, bid=bid_array, ask=ask_array, bid_size=bid_size,
                     ask_size=ask_size, depth=10)


def traderRowParser(row):
    if row[1][0] == 'T':
        volPrice = row[1][1:]
        volume, price = re.split('@', volPrice)
        return Trade(instrument='Test', timestamp=datetime.strptime(row[0], '%Y%m%d%H%M%S%f'), price=price, size=volume)
    else:
        return None


# with open(os.path.join(directory, datfile), 'rb') as csvfile:
#     reader = csv.reader(csvfile, delimiter=' ')
#     for row in reader:
#         if row[1][0] == 'B' :
#             print orderBookRowParser(row)
#         elif row[1][0] == 'T' :
#             print traderRowParser(row)


# sampleQuoteRow = ['20130717093442335', 'B79800@1.7976931348623e+308', 'B3500@165', 'B26000@160', 'B200@158', 'B36000@157.5', 'B0@0', 'B0@0', 'B0@0', 'B0@0', 'B0@0', 'A110700@1.7976931348623e+308', 'A100@129', 'A3500@155', 'A900@156', 'A20300@156.5', 'A0@0', 'A0@0', 'A0@0', 'A0@0', 'A0@0']
# sampleTradeRow = ['20130717093523396', 'T153800@156.5']
# traderRowParser(sampleTradeRow)
# orderBookRowParser(sampleQuoteRow)

class DecideDataFeed(object):
    def __init__(self, directory, datfile, subject=None):
        if not subject:
            subject = EventBus.data_subject
        self.subject = subject
        self.directory = directory
        self.datfile = datfile
        # self.dfs = []
        # for name in names:
        #     df = self.read_csv(name, '../../data/%s.csv' % name)
        #     self.dfs.append(df)

        # self.df = pd.concat(self.dfs).sort_index(0, ascending=True)

    def start(self):
        with open(os.path.join(self.directory, self.datfile), 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            for row in reader:
                if row[1][0] == 'B':
                    self.subject.on_next(orderBookRowParser(row))
                elif row[1][0] == 'T':
                    self.subject.on_next(traderRowParser(row))

    def stop(self):
        pass

    def id(self):
        return "DecideFeed"

    @staticmethod
    def read_csv(symobl, file):
        df = pd.read_csv(file, index_col='Date', parse_dates=['Date'], date_parser=dateparse)
        df['Symbol'] = symobl
        df['BarSize'] = int(BarSize.D1)
        return df

# def decideGenerator(directory, datfile):
#    with open(os.path.join(directory, datfile), 'rb') as csvfile:
#        reader = csv.reader(csvfile, delimiter=' ')
#        for row in reader:
#            if row[1][0] == 'B' :
#                yield orderBookRowParser(row)
#            elif row[1][0] == 'T' :
#                yield traderRowParser(row)


# import itertools
#
# generator = decideGenerator(directory, datfile)
# top10 = itertools.islice(generator, 10)
# itertools.islice(generator, 1000)
#
# alist = list( itertools.islice(generator, 1000))
#
# o = alist[0]
# type(o) is OrderBook
#
# trades = [ x for x in decideGenerator(directory, datfile) if type(x) is Trade]
# t = trades[0]
# t.price
# tradesPrice = [ t.price for t in trades ]
# import pandas as pd
# ts = pd.Series(np.array(tradesPrice, dtype='float'))
#
# ts.tail(100).plot()
# import matplotlib.pyplot as plt
# ts.plot()
# plt.show()
#
# ts.describe()
# class FooA(object) :
#     def __init__(self,x):
#         self.x = x
#
# class FooB(object) :
#     def __init__(self, x):
#         self.x = x
#
# def testGen(len) :
#     for i in range(len) :
#         if i % 2 == 0 :
#             yield FooA(i)
#         else :
#             yield FooB(i)


# list(testGen(10))


# import itertools
# top10 = itertools.islice(list(testGen(100)), 10)
# top10 = itertools.islice(testGen(100), 10)
