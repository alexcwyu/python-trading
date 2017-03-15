import abc

from algotrader.event.event_handler import MarketDataEventHandler
from algotrader.model.market_data_pb2 import *
from algotrader.model.trade_data_pb2 import *
from algotrader.model.trading.order import Order

from algotrader.model.model_helper import ModelHelper

class HasPositions(MarketDataEventHandler):
    __metaclass__ = abc.ABCMeta

    def get_position(self, inst_id: str) -> Position:
        if inst_id not in self.state.positions:
            #self.state.positions[inst_id] = self.model_factory.build_position(inst_id=inst_id)
            position = self.state.positions[inst_id]
            position.CopyFrom(self.model_factory.build_position(inst_id=inst_id))
        position = self.state.positions[inst_id]
        return position

    def update_position_price(self, timestamp: int, inst_id: str, price: float) -> None:
        if inst_id in self.state.positions:
            position = self.state.positions[inst_id]
            position.last_price = price

    def add_position(self, inst_id: str, cl_id: str, cl_req_id: str, qty: float) -> None:
        position = self.get_position(inst_id)
        order_position = self.__get_or_add_order(position=position, cl_id=cl_id,
                                                 cl_req_id=cl_req_id)
        order_position.filled_qty = qty
        position.filled_qty += qty

    def add_order(self, inst_id: str, cl_id: str, cl_req_id: str, ordered_qty: float) -> None:
        #self.state.cl_orders.extends()
        ModelHelper.add_to_list(self.state.cl_orders, [self.model_factory.build_client_order_id(cl_id = cl_id, cl_req_id = cl_req_id)])


        position = self.get_position(inst_id)
        order_position = self.__get_or_add_order(position=position, cl_id=cl_id,
                                                 cl_req_id=cl_req_id)
        order_position.ordered_qty = ordered_qty
        position.ordered_qty += ordered_qty

    def __get_or_add_order(self, position: Position, cl_id: str, cl_req_id: str) -> OrderPosition:
        id = cl_id + "@" + cl_req_id
        if id not in position.orders:
            order = position.orders[id]
            order.CopyFrom(self.model_factory.build_order_position(cl_id=cl_id,
                                                                    cl_req_id=cl_req_id,
                                                                    ordered_qty=0, filled_qty=0))
        return position.orders[id]

    def on_bar(self, bar: Bar) -> None:
        self.update_position_price(bar.timestamp, bar.inst_id, bar.close)

    def on_quote(self, quote: Quote) -> None:
        self.update_position_price(quote.timestamp, quote.inst_id, quote.mid())

    def on_trade(self, trade: Trade) -> None:
        self.update_position_price(trade.timestamp, trade.inst_id, trade.price)

    def position_filled_qty(self, inst_id: str) -> float:
        position = self.get_position(inst_id)
        return position.filled_qty

    def position_ordered_qty(self, inst_id: str) -> float:
        position = self.get_position(inst_id)
        return position.ordered_qty

    def position_value(self, inst_id: str) -> float:
        position = self.get_position(inst_id)
        return position.last_price * position.filled_qty

    def total_value(self) -> float:
        total = 0
        for inst_id, position in self.state.positions.items():
            total += self.position_value(inst_id)
        return total
