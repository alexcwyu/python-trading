from unittest import TestCase

from algotrader.event.order import NewOrderRequest, OrdAction, OrdType, ExecutionReport, OrdStatus, Order
from algotrader.trading.position import Position


class PositionTest(TestCase):
    def test_add_order(self):
        position = Position(1)
        self.assertEquals(0, position.filled_qty())
        self.assertEquals(0, len(position.all_orders()))

        order1 = Order(NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5))
        position.add_order(order1)

        self.assertEquals(1000, position.ordered_qty())
        self.assertEquals(1, len(position.all_orders()))

        order2 = Order(NewOrderRequest(cl_id='test', cl_ord_id=2, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5))
        position.add_order(order2)

        self.assertEquals(2000, position.ordered_qty())
        self.assertEquals(2, len(position.all_orders()))

        order3 = Order(NewOrderRequest(cl_id='test', cl_ord_id=3, inst_id=1, action=OrdAction.SELL, type=OrdType.LIMIT, qty=1200,
                                limit_price=18.5))
        position.add_order(order3)

        self.assertEquals(800, position.ordered_qty())
        self.assertEquals(3, len(position.all_orders()))

    def test_add_order_with_same_ord_id(self):
        position = Position(1)
        order1 = Order(NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5))
        order2 = Order(NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5))

        position.add_order(order1)

        with self.assertRaises(RuntimeError) as ex:
            position.add_order(order2)

    def test_add_order_with_diff_inst(self):
        position = Position(1)
        order1 = Order(NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5))
        order2 = Order(NewOrderRequest(cl_id='test', cl_ord_id=2, inst_id=2, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                                limit_price=18.5))

        position.add_order(order1)

        with self.assertRaises(RuntimeError) as ex:
            position.add_order(order2)

    def test_fill_qty(self):
        position = Position(1)
        self.assertEquals(0, position.filled_qty())

        order1 = Order(NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5))
        position.add_order(order1)
        self.assertEquals(0, position.filled_qty())

        er1 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=1, inst_id=1, last_qty=500, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        order1.on_exec_report(er1)
        position.add_position(er1.cl_id, er1.cl_ord_id, er1.last_qty)
        self.assertEquals(500, position.filled_qty())

        er2 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=2, inst_id=1, last_qty=500, last_price=18.4,
                              status=OrdStatus.FILLED)
        order1.on_exec_report(er2)
        position.add_position(er2.cl_id, er2.cl_ord_id, er2.last_qty)
        self.assertEquals(1000, position.filled_qty())

        order2 = Order(NewOrderRequest(cl_id='test', cl_ord_id=2, inst_id=1, action=OrdAction.SELL, type=OrdType.LIMIT, qty=1200,
                                limit_price=18.5))
        position.add_order(order2)
        self.assertEquals(1000, position.filled_qty())

        er3 = ExecutionReport(cl_id='test', cl_ord_id=2, ord_id=2, er_id=3, inst_id=1, last_qty=800, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        order2.on_exec_report(er3)
        position.add_position(er3.cl_id, er3.cl_ord_id, er3.last_qty * -1)
        self.assertEquals(200, position.filled_qty())

        er4 = ExecutionReport(cl_id='test', cl_ord_id=2, ord_id=2, er_id=4, inst_id=1, last_qty=400, last_price=18.4,
                              status=OrdStatus.FILLED)
        order2.on_exec_report(er4)
        position.add_position(er4.cl_id, er4.cl_ord_id, er4.last_qty * -1)
        self.assertEquals(-200, position.filled_qty())
