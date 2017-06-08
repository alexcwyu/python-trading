import abc

from algotrader.model.market_data_pb2 import *
from algotrader.model.model_factory import ModelFactory
from algotrader.model.trade_data_pb2 import *
from algotrader.trading.event import MarketDataEventHandler
from algotrader.utils.market_data import get_quote_mid
from algotrader.utils.model import add_to_list


class HasPositions(MarketDataEventHandler):
    __metaclass__ = abc.ABCMeta

    def __init__(self, state):
        self.state = state

    def positions(self):
        return self.state.positions

    def has_position(self, inst_id: str) -> bool:
        return inst_id in self.state.positions

    def get_position(self, inst_id: str) -> Position:
        if inst_id not in self.state.positions:
            ModelFactory.add_position(self.state, inst_id=inst_id)
        position = self.state.positions[inst_id]
        return position

    def update_price(self, timestamp: int, inst_id: str, price: float) -> None:
        if inst_id in self.state.positions:
            position = self.state.positions[inst_id]
            position.last_price = price

    def add_position(self, inst_id: str, cl_id: str, cl_ord_id: str, qty: float) -> None:
        position = self.get_position(inst_id)
        order_position = self.__get_or_add_order(position=position, cl_id=cl_id,
                                                 cl_ord_id=cl_ord_id)
        order_position.filled_qty = qty
        position.filled_qty += qty

    def add_order(self, inst_id: str, cl_id: str, cl_ord_id: str, ordered_qty: float) -> None:
        add_to_list(self.state.cl_ord_ids, [cl_ord_id])

        position = self.get_position(inst_id)
        order_position = self.__get_or_add_order(position=position, cl_id=cl_id,
                                                 cl_ord_id=cl_ord_id)
        order_position.ordered_qty = ordered_qty
        position.ordered_qty += ordered_qty

    def __get_or_add_order(self, position: Position, cl_id: str, cl_ord_id: str) -> OrderPosition:
        id = ModelFactory.build_cl_ord_id(cl_id, cl_ord_id)
        if id not in position.orders:
            ModelFactory.add_order_position(position, cl_id=cl_id,
                                            cl_ord_id=cl_ord_id,
                                            ordered_qty=0, filled_qty=0)
        return position.orders[id]

    def on_bar(self, bar: Bar) -> None:
        self.update_price(bar.timestamp, bar.inst_id, bar.close)

    def on_quote(self, quote: Quote) -> None:
        self.update_price(quote.timestamp, quote.inst_id, get_quote_mid(quote))

    def on_trade(self, trade: Trade) -> None:
        self.update_price(trade.timestamp, trade.inst_id, trade.price)

    def position_filled_qty(self, inst_id: str) -> float:
        position = self.get_position(inst_id)
        return position.filled_qty

    def position_ordered_qty(self, inst_id: str) -> float:
        position = self.get_position(inst_id)
        return position.ordered_qty

    def position_value(self, inst_id: str) -> float:
        position = self.get_position(inst_id)
        return position.last_price * position.filled_qty

    def total_position_value(self) -> float:
        total = 0
        for inst_id, position in self.state.positions.items():
            total += self.position_value(inst_id)
        return total

    def position_order_ids(self, inst_id: str):
        if not self.has_position(inst_id):
            return []

        position = self.get_position(inst_id)
        return [ord_id for ord_id in position.orders.keys()]
