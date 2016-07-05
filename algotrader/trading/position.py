from algotrader.event.order import OrdAction
from algotrader.event.market_data import MarketDataEventHandler
from collections import defaultdict


class Position(object):
    def __init__(self, inst_id):
        self.inst_id = inst_id
        self.orders = defaultdict(dict)
        self.ordered_size = 0
        self.filled_qty_dict = {}
        self.last_price = 0

    def add_order(self, order):
        if order.inst_id != self.inst_id:
            raise RuntimeError("order[%s][%s] inst_id [%s] is not same as inst_id [%s] of position" % (
                order.cl_id, order.cl_ord_id, order.inst_id, self.inst_id))

        if order.cl_ord_id in self.orders[order.cl_id]:
            raise RuntimeError("order[%s][%s] already exist" % (order.cl_id, order.cl_ord_id))
        self.orders[order.cl_id][order.cl_ord_id] = order
        self.ordered_size += order.qty if order.action == OrdAction.BUY else -order.qty

    def add_position(self, ord_id, filled_qty):
        existing_filled_qty = self.filled_qty_dict.get(ord_id, 0)
        total_filled_qty = existing_filled_qty + filled_qty
        self.filled_qty_dict[ord_id] = total_filled_qty

    def total_qty(self):
        qty = 0
        for filled_qty in self.filled_qty_dict.values():
            qty += filled_qty
        return qty

    def current_value(self):
        return self.last_price * self.total_qty()

    def all_orders(self):
        return [order for cl_orders in self.orders.values() for order in cl_orders.values()]

    def __repr__(self):
        return "Position(inst_id=%s, orders=%s, size=%s, last_price=%s)" % (
            self.inst_id, self.orders, self.size, self.last_price
        )


class PositionHolder(MarketDataEventHandler):
    def __init__(self):
        self.positions = {}

    def get_position(self, inst_id):
        if inst_id not in self.positions:
            self.positions[inst_id] = Position(inst_id=inst_id)
        position = self.positions[inst_id]
        return position

    # def add_order_to_position(self, order):
    #     if order.inst_id not in self.positions:
    #         self.positions[order.inst_id] = Position(inst_id=order.inst_id)
    #     position = self.positions[order.inst_id]
    #     position.add_order(order)
    #     return position

    def update_position_price(self, time, inst_id, price):
        if inst_id in self.positions:
            position = self.positions[inst_id]
            position.last_price = price

    def add_positon(self, inst_id, ord_id, qty):
        position = self.get_position(inst_id)
        position.add_position(ord_id, qty)

    def on_bar(self, bar):
        self.update_position_price(bar.timestamp, bar.inst_id, bar.close)

    def on_quote(self, quote):
        self.update_position_price(quote.timestamp, quote.inst_id, quote.mid())

    def on_trade(self, trade):
        self.update_position_price(trade.timestamp, trade.inst_id, trade.price)
