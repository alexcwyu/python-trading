import pyfolio as pf

# stock_rets = pf.utils.get_symbol_rets('SPY')
stock_rets = pf.utils.get_symbol_rets('FB')
print type(stock_rets)

from pandas_datareader import data as web

px = web.get_data_yahoo('FB', start=None, end=None)
rets = px[['Adj Close']].pct_change().dropna()
rets.index = rets.index.tz_localize("UTC")
rets.columns = ['FB']
print type(rets)

rets = rets['FB']
print type(rets)
print stock_rets

print "###"
print rets

pf.create_returns_tear_sheet(stock_rets)

import matplotlib.pyplot as plt

plt.show()
