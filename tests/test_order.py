from unittest import TestCase

from algotrader.event.order import NewOrderRequest, OrdAction, OrdType, OrdStatus, OrderStatusUpdate, ExecutionReport
from algotrader.trading.order import Order


class OrderTest(TestCase):
    def test_is_buy(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        self.assertTrue(order.is_buy())
        self.assertFalse(order.is_sell())

    def test_is_sell(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.SELL, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        self.assertFalse(order.is_buy())
        self.assertTrue(order.is_sell())

        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.SSHORT, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        self.assertFalse(order.is_buy())
        self.assertTrue(order.is_sell())

    def test_is_done(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        self.assertFalse(order.is_done())

        status_update1 = OrderStatusUpdate(cl_id='test', cl_ord_id=1, ord_id=1, inst_id=1, status=OrdStatus.REJECTED)
        order.on_ord_upd(status_update1)
        self.assertTrue(order.is_done())

        order2 = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=2, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        status_update2 = OrderStatusUpdate(cl_id='test', cl_ord_id=2, ord_id=2, inst_id=1, status=OrdStatus.CANCELLED)
        order2.on_ord_upd(status_update2)
        self.assertTrue(order2.is_done())

        order3 = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=3, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        status_update3 = OrderStatusUpdate(cl_id='test', cl_ord_id=3, ord_id=3, inst_id=1, status=OrdStatus.FILLED)
        order3.on_ord_upd(status_update3)
        self.assertTrue(order3.is_done())

    def test_is_active(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        self.assertTrue(order.is_active())

    def test_leave_qty(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        self.assertEqual(1000, order.leave_qty())

        er1 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=1, inst_id=1, last_qty=800, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        order.on_exec_report(er1)
        self.assertEqual(200, order.leave_qty())

        er2 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=2, inst_id=1, last_qty=200, last_price=18.4,
                              status=OrdStatus.FILLED)
        order.on_exec_report(er2)
        self.assertEqual(0, order.leave_qty())
        self.assertTrue(order.is_done())
        self.assertEquals(OrdStatus.FILLED, order.status)

    def test_on_ord_upd(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        self.assertEquals(OrdStatus.NEW, order.status)

        status_update = OrderStatusUpdate(cl_id='test', cl_ord_id=1, ord_id=1, inst_id=1, status=OrdStatus.SUBMITTED)
        order.on_ord_upd(status_update)

        self.assertEqual(status_update.ord_id, order.broker_ord_id)
        self.assertEquals(OrdStatus.SUBMITTED, order.status)

    def test_update_status_with_diff_cl_ord_id(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        self.assertEquals(OrdStatus.NEW, order.status)

        status_update = OrderStatusUpdate(cl_id='test', cl_ord_id=2, ord_id=2, inst_id=1, status=OrdStatus.SUBMITTED)

        with self.assertRaises(Exception) as ex:
            order.on_ord_upd(status_update)

    def test_update_status_with_diff_ord_id(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        self.assertEquals(OrdStatus.NEW, order.status)

        status_update = OrderStatusUpdate(cl_id='test', cl_ord_id=1, ord_id=2, inst_id=1, status=OrdStatus.SUBMITTED)
        order.on_ord_upd(status_update)

        status_update = OrderStatusUpdate(cl_id='test', cl_ord_id=1, ord_id=3, inst_id=1, status=OrdStatus.SUBMITTED)
        with self.assertRaises(Exception) as ex:
            order.on_ord_upd(status_update)

    def test_exec_report(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))
        self.assertEqual(1000, order.leave_qty())
        self.assertEqual(0, len(order.get_events(ExecutionReport)))

        er1 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=1, inst_id=1, last_qty=800, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        order.on_exec_report(er1)
        self.assertEqual(1, len(order.get_events(ExecutionReport)))
        self.assertTrue(er1 in order.get_events(ExecutionReport))

        self.assertEqual(er1.ord_id, order.broker_ord_id)
        self.assertEqual(800, order.last_qty)
        self.assertAlmostEqual(18.4, order.last_price)
        self.assertEqual(800, order.filled_qty)
        self.assertAlmostEqual(18.4, order.avg_price)
        self.assertEqual(OrdStatus.PARTIALLY_FILLED, order.status)

        er2 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=2, inst_id=1, last_qty=200, last_price=18.4,
                              status=OrdStatus.FILLED)
        order.on_exec_report(er2)
        self.assertEqual(2, len(order.get_events(ExecutionReport)))
        self.assertTrue(er1 in order.get_events(ExecutionReport))
        self.assertTrue(er2 in order.get_events(ExecutionReport))

        self.assertEqual(er2.ord_id, order.broker_ord_id)
        self.assertEqual(200, order.last_qty)
        self.assertAlmostEqual(18.4, order.last_price)
        self.assertEqual(1000, order.filled_qty)
        self.assertAlmostEqual(18.4, order.avg_price)
        self.assertEqual(OrdStatus.FILLED, order.status)

    def test_exec_report_with_diff_ord_id(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))

        er1 = ExecutionReport(cl_id='test', cl_ord_id=2, ord_id=2, er_id=1, inst_id=1, last_qty=800, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)

        with self.assertRaises(Exception) as ex:
            order.on_exec_report(er1)

    def test_exec_report_with_exceed_qty(self):
        order = Order(
            NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                            limit_price=18.5))

        er1 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=1, inst_id=1, last_qty=800, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        order.on_exec_report(er1)

        er2 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=2, inst_id=1, last_qty=200, last_price=18.4,
                              status=OrdStatus.FILLED)
        order.on_exec_report(er2)

        er3 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=3, inst_id=1, last_qty=100, last_price=18.4,
                              status=OrdStatus.FILLED)
        with self.assertRaises(Exception) as ex:
            order.on_exec_report(er3)
