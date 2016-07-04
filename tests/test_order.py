from unittest import TestCase

from algotrader.event.order import NewOrderSingle, OrdAction, OrdType, OrdStatus, OrderStatusUpdate, ExecutionReport


class OrderTest(TestCase):
    def test_is_done(self):
        order = NewOrderSingle(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        self.assertFalse(order.is_done())

        status_update1 = OrderStatusUpdate(ord_id=1, inst_id=1, status=OrdStatus.REJECTED)
        order.update_status(status_update1)
        self.assertTrue(order.is_done())

        order2 = NewOrderSingle(ord_id=2, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        status_update2 = OrderStatusUpdate(ord_id=2, inst_id=1, status=OrdStatus.CANCELLED)
        order2.update_status(status_update2)
        self.assertTrue(order2.is_done())

        order3 = NewOrderSingle(ord_id=3, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        status_update3 = OrderStatusUpdate(ord_id=3, inst_id=1, status=OrdStatus.FILLED)
        order3.update_status(status_update3)
        self.assertTrue(order3.is_done())

    def test_is_active(self):
        order = NewOrderSingle(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        self.assertTrue(order.is_active())

    def test_leave_qty(self):
        order = NewOrderSingle(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        self.assertEqual(1000, order.leave_qty())

        er1 = ExecutionReport(ord_id=1, er_id=1, inst_id=1, last_qty=800, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        order.add_exec_report(er1)
        self.assertEqual(200, order.leave_qty())

        er2 = ExecutionReport(ord_id=1, er_id=2, inst_id=1, last_qty=200, last_price=18.4,
                              status=OrdStatus.FILLED)
        order.add_exec_report(er2)
        self.assertEqual(0, order.leave_qty())
        self.assertTrue(order.is_done())
        self.assertEquals(OrdStatus.FILLED, order.status)

    def test_update_status(self):
        order = NewOrderSingle(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        self.assertEquals(OrdStatus.NEW, order.status)

        status_update = OrderStatusUpdate(ord_id=1, inst_id=1, status=OrdStatus.SUBMITTED)
        order.update_status(status_update)

        self.assertEquals(OrdStatus.SUBMITTED, order.status)

    def test_update_status_with_diff_ord_id(self):
        order = NewOrderSingle(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        self.assertEquals(OrdStatus.NEW, order.status)

        status_update = OrderStatusUpdate(ord_id=2, inst_id=1, status=OrdStatus.SUBMITTED)

        with self.assertRaises(Exception) as ex:
            order.update_status(status_update)

    def test_exec_report(self):
        order = NewOrderSingle(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        self.assertEqual(1000, order.leave_qty())
        self.assertEqual(0, len(order.exec_reports))

        er1 = ExecutionReport(ord_id=1, er_id=1, inst_id=1, last_qty=800, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        order.add_exec_report(er1)
        self.assertEqual(1, len(order.exec_reports))
        self.assertTrue(er1 in order.exec_reports)

        er2 = ExecutionReport(ord_id=1, er_id=2, inst_id=1, last_qty=200, last_price=18.4,
                              status=OrdStatus.FILLED)
        order.add_exec_report(er2)
        self.assertEqual(2, len(order.exec_reports))
        self.assertTrue(er1 in order.exec_reports)
        self.assertTrue(er2 in order.exec_reports)

    def test_exec_report_with_diff_ord_id(self):
        order = NewOrderSingle(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)

        er1 = ExecutionReport(ord_id=2, er_id=1, inst_id=1, last_qty=800, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)

        with self.assertRaises(Exception) as ex:
            order.add_exec_report(er1)

    def test_exec_report_with_exceed_qty(self):
        order = NewOrderSingle(ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)

        er1 = ExecutionReport(ord_id=1, er_id=1, inst_id=1, last_qty=800, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        order.add_exec_report(er1)

        er2 = ExecutionReport(ord_id=1, er_id=2, inst_id=1, last_qty=200, last_price=18.4,
                              status=OrdStatus.FILLED)
        order.add_exec_report(er2)

        er3 = ExecutionReport(ord_id=1, er_id=3, inst_id=1, last_qty=100, last_price=18.4,
                              status=OrdStatus.FILLED)
        with self.assertRaises(Exception) as ex:
            order.add_exec_report(er3)
