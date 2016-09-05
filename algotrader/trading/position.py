from algotrader.event.event_handler import MarketDataEventHandler
from algotrader.event.order import OrdAction
from algotrader.provider.persistence import Persistable


class Position(Persistable):
    __slots__ = (
        'inst_id',
        'orders',
        'filled_qty_dict',
        'last_price'
    )

    def __init__(self, inst_id=None):
        self.inst_id = inst_id
        self.orders = {}
        self.filled_qty_dict = {}
        self.last_price = 0

    def add_order(self, order):
        if order.inst_id != self.inst_id:
            raise RuntimeError("order[%s][%s] inst_id [%s] is not same as inst_id [%s] of position" % (
                order.cl_id, order.cl_ord_id, order.inst_id, self.inst_id))

        if order.cl_id not in self.orders:
            self.orders[order.cl_id] = {}

        if order.cl_ord_id in self.orders[order.cl_id]:
            raise RuntimeError("order[%s][%s] already exist" % (order.cl_id, order.cl_ord_id))

        self.orders[order.cl_id][order.cl_ord_id] = order

    def add_position(self, cl_id, cl_ord_id, filled_qty):
        if cl_id not in self.filled_qty_dict:
            self.filled_qty_dict[cl_id] = {}
        existing_filled_qty = self.filled_qty_dict[cl_id].get(cl_ord_id, 0)
        updated_filled_qty = existing_filled_qty + filled_qty
        self.filled_qty_dict[cl_id][cl_ord_id] = updated_filled_qty

    def filled_qty(self):
        total = 0
        for cl_id, cl_filled_qty_dict in self.filled_qty_dict.iteritems():
            for cl_ord_id, reg_qty in cl_filled_qty_dict.iteritems():
                total += reg_qty
        return total

    def ordered_qty(self):
        total = 0
        for cl_orders in self.orders.values():
            for order in cl_orders.values():
                total += order.qty if order.action == OrdAction.BUY else -order.qty
        return total

    def current_value(self):
        return self.last_price * self.filled_qty()

    def all_orders(self):
        return [order for cl_orders in self.orders.values() for order in cl_orders.values()]

    def id(self):
        return self.inst_id


class PositionHolder(MarketDataEventHandler):
    __slots__ = (
        'positions'
    )

    def __init__(self):
        self.positions = {}

    def get_position(self, inst_id):
        if inst_id not in self.positions:
            self.positions[inst_id] = Position(inst_id=inst_id)
        position = self.positions[inst_id]
        return position

    def update_position_price(self, time, inst_id, price):
        if inst_id in self.positions:
            position = self.positions[inst_id]
            position.last_price = price

    def add_position(self, inst_id, cl_id, cl_ord_id, qty):
        position = self.get_position(inst_id)
        position.add_position(cl_id, cl_ord_id, qty)

    def on_bar(self, bar):
        self.update_position_price(bar.timestamp, bar.inst_id, bar.close)

    def on_quote(self, quote):
        self.update_position_price(quote.timestamp, quote.inst_id, quote.mid())

    def on_trade(self, trade):
        self.update_position_price(trade.timestamp, trade.inst_id, trade.price)
