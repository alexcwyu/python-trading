import zerorpc

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.event.order import Order, OrdAction, OrdType

c = zerorpc.Client()
c.connect("tcp://127.0.0.1:14242")

bar = Bar(open=18, high=19, low=17, close=17.5, vol=1000)
quote = Quote(bid=18, ask=19, bid_size=200, ask_size=500)
trade = Trade(price=20, size=200)
order = Order(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)

print c.on_order(order)
