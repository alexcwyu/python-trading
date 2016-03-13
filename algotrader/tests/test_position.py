from unittest import TestCase

from algotrader.event.order import Order, OrdAction, OrdType, ExecutionReport, OrdStatus
from algotrader.trading.portfolio import Position


class PositionTest(TestCase):
    def test_add_order(self):
        position = Position('HSI')
        self.assertEquals(0, position.size)
        self.assertEquals(0, len(position.orders))

        order1 = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        position.add_order(order1)

        self.assertEquals(1000, position.size)
        self.assertEquals(1, len(position.orders))

        order2 = Order(ord_id=2, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        position.add_order(order2)

        self.assertEquals(2000, position.size)
        self.assertEquals(2, len(position.orders))

        order3 = Order(ord_id=3, instrument="HSI", action=OrdAction.SELL, type=OrdType.LIMIT, qty=1200,
                       limit_price=18.5)
        position.add_order(order3)

        self.assertEquals(800, position.size)
        self.assertEquals(3, len(position.orders))

    def test_add_order_with_same_ord_id(self):
        position = Position('HSI')
        order1 = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        order2 = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)

        position.add_order(order1)

        with self.assertRaises(RuntimeError) as ex:
            position.add_order(order2)


    def test_add_order_with_diff_inst(self):
        position = Position('HSI')
        order1 = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        order2 = Order(ord_id=2, instrument="HSI2", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                       limit_price=18.5)

        position.add_order(order1)

        with self.assertRaises(RuntimeError) as ex:
            position.add_order(order2)


    def test_fill_qty(self):
        position = Position('HSI')
        self.assertEquals(0, position.filled_qty())

        order1 = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        position.add_order(order1)
        self.assertEquals(0, position.filled_qty())

        er1 = ExecutionReport(ord_id=1, er_id=1, instrument="HSI", filled_qty=500, filled_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        order1.add_exec_report(er1)
        self.assertEquals(500, position.filled_qty())


        er2 = ExecutionReport(ord_id=1, er_id=2, instrument="HSI", filled_qty=500, filled_price=18.4,
                              status=OrdStatus.FILLED)
        order1.add_exec_report(er2)
        self.assertEquals(1000, position.filled_qty())


        order2 = Order(ord_id=2, instrument="HSI", action=OrdAction.SELL, type=OrdType.LIMIT, qty=1200, limit_price=18.5)
        position.add_order(order2)
        self.assertEquals(1000, position.filled_qty())

        er3 = ExecutionReport(ord_id=2, er_id=3, instrument="HSI", filled_qty=800, filled_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        order2.add_exec_report(er3)
        self.assertEquals(200, position.filled_qty())


        er4 = ExecutionReport(ord_id=2, er_id=4, instrument="HSI", filled_qty=400, filled_price=18.4,
                              status=OrdStatus.FILLED)
        order2.add_exec_report(er4)
        self.assertEquals(-200, position.filled_qty())