from unittest import TestCase

from algotrader.model.model_factory import ModelFactory
from algotrader.model.trade_data_pb2 import *
from algotrader.trading.order import Order


class OrderTest(TestCase):
    def test_is_buy(self):
        nos = ModelFactory.build_new_order_request(timestamp=0,
                                                   cl_id='TestClient', cl_ord_id="TestClientOrder",
                                                   portf_id="TestPortf", broker_id="TestBroker",
                                                   inst_id="HSI@SEHK", action=Buy, type=Limit, qty=1000,
                                                   limit_price=18.5)
        order = Order(ModelFactory.build_order_state_from_nos(nos))
        self.assertTrue(order.is_buy())
        self.assertFalse(order.is_sell())

    def test_is_sell(self):
        nos = ModelFactory.build_new_order_request(timestamp=0,
                                                   cl_id='TestClient', cl_ord_id="TestClientOrder",
                                                   portf_id="TestPortf", broker_id="TestBroker",
                                                   inst_id="HSI@SEHK", action=Sell, type=Limit, qty=1000,
                                                   limit_price=18.5)
        order = Order(ModelFactory.build_order_state_from_nos(nos))
        self.assertFalse(order.is_buy())
        self.assertTrue(order.is_sell())

    def test_is_done(self):
        order1 = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="1",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))

        status_update1 = ModelFactory.build_order_status_update(timestamp=0,
                                                                broker_id="TestBroker",
                                                                broker_event_id="1",
                                                                broker_ord_id="1",
                                                                cl_id='TestClient', cl_ord_id="1",
                                                                status=Rejected)

        order1.on_ord_upd(status_update1)
        self.assertTrue(order1.is_done())

        order2 = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="2",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))

        status_update2 = ModelFactory.build_order_status_update(timestamp=0,
                                                                broker_id="TestBroker",
                                                                broker_event_id="2",
                                                                broker_ord_id="2",
                                                                cl_id='TestClient', cl_ord_id="2",
                                                                status=Cancelled)

        order2.on_ord_upd(status_update2)
        self.assertTrue(order1.is_done())

        order3 = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="3",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))

        status_update3 = ModelFactory.build_order_status_update(timestamp=0,
                                                                broker_id="TestBroker",
                                                                broker_event_id="3",
                                                                broker_ord_id="3",
                                                                cl_id='TestClient', cl_ord_id="3",
                                                                status=Filled)

        order3.on_ord_upd(status_update3)
        self.assertTrue(order3.is_done())

    def test_is_active(self):
        order1 = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="1",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))

        self.assertTrue(order1.is_active())

    def test_leave_qty(self):
        order = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="1",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))
        self.assertEqual(1000, order.leave_qty())

        er1 = ModelFactory.build_execution_report(timestamp=0, broker_id="TestBroker",
                                                  broker_event_id="1",
                                                  broker_ord_id="1",
                                                  cl_id='TestClient', cl_ord_id="1", inst_id="HSI@SEHK", last_qty=800,
                                                  last_price=18.4,
                                                  status=PartiallyFilled)
        order.on_exec_report(er1)
        self.assertEqual(200, order.leave_qty())

        er2 = ModelFactory.build_execution_report(timestamp=0, broker_id="TestBroker",
                                                  broker_event_id="2",
                                                  broker_ord_id="1",
                                                  cl_id='TestClient', cl_ord_id="1", inst_id="HSI@SEHK", last_qty=200,
                                                  last_price=18.4,
                                                  status=Filled)
        order.on_exec_report(er2)
        self.assertEqual(0, order.leave_qty())
        self.assertTrue(order.is_done())
        self.assertEquals(Filled, order.status())

    def test_on_ord_upd(self):
        order = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="3",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))

        status_update = ModelFactory.build_order_status_update(timestamp=0,
                                                               broker_id="TestBroker",
                                                               broker_event_id="3",
                                                               broker_ord_id="3",
                                                               cl_id='TestClient', cl_ord_id="3",
                                                               status=Submitted)

        order.on_ord_upd(status_update)
        self.assertEqual(status_update.broker_ord_id, order.broker_ord_id())
        self.assertEquals(Submitted, order.status())

    def test_update_status_with_diff_cl_ord_id(self):
        order = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="3",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))

        self.assertEquals(New, order.status())

        status_update = ModelFactory.build_order_status_update(timestamp=0,
                                                               broker_id="TestBroker",
                                                               broker_event_id="3",
                                                               broker_ord_id="3",
                                                               cl_id='TestClient', cl_ord_id="ERROR",
                                                               status=Submitted)

        with self.assertRaises(Exception) as ex:
            order.on_ord_upd(status_update)

    def test_update_status_with_diff_ord_id(self):
        order = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="3",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))

        self.assertEquals(New, order.status())

        status_update1 = ModelFactory.build_order_status_update(timestamp=0,
                                                                broker_id="TestBroker",
                                                                broker_event_id="3",
                                                                broker_ord_id="3",
                                                                cl_id='TestClient', cl_ord_id="3",
                                                                status=Submitted)

        order.on_ord_upd(status_update1)
        self.assertEquals(Submitted, order.status())

        status_update2 = ModelFactory.build_order_status_update(timestamp=0,
                                                                broker_id="TestBroker",
                                                                broker_event_id="3",
                                                                broker_ord_id="ERROR",
                                                                cl_id='TestClient', cl_ord_id="3",
                                                                status=Filled)

        with self.assertRaises(Exception) as ex:
            order.on_ord_upd(status_update2)

    def test_exec_report(self):
        order = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="1",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))

        self.assertEqual(1000, order.leave_qty())
        self.assertEqual(0, len(order.get_events(ExecutionReport)))

        er1 = ModelFactory.build_execution_report(timestamp=0, broker_id="TestBroker",
                                                  broker_event_id="1",
                                                  broker_ord_id="1",
                                                  cl_id='TestClient', cl_ord_id="1", inst_id="HSI@SEHK", last_qty=800,
                                                  last_price=18.4,
                                                  status=PartiallyFilled)
        order.on_exec_report(er1)
        self.assertEqual(1, len(order.get_events(ExecutionReport)))
        self.assertTrue(er1 in order.get_events(ExecutionReport))

        self.assertEqual(er1.broker_ord_id, order.broker_ord_id())
        self.assertEqual(800, order.last_qty())
        self.assertAlmostEqual(18.4, order.last_price())
        self.assertEqual(800, order.filled_qty())
        self.assertAlmostEqual(18.4, order.avg_price())
        self.assertEqual(PartiallyFilled, order.status())

        er2 = ModelFactory.build_execution_report(timestamp=0, broker_id="TestBroker",
                                                  broker_event_id="1",
                                                  broker_ord_id="1",
                                                  cl_id='TestClient', cl_ord_id="1", inst_id="HSI@SEHK", last_qty=200,
                                                  last_price=18.4,
                                                  status=Filled)
        order.on_exec_report(er2)
        self.assertEqual(2, len(order.get_events(ExecutionReport)))
        self.assertTrue(er1 in order.get_events(ExecutionReport))
        self.assertTrue(er2 in order.get_events(ExecutionReport))

        self.assertEqual(er2.broker_ord_id, order.broker_ord_id())
        self.assertEqual(200, order.last_qty())
        self.assertAlmostEqual(18.4, order.last_price())
        self.assertEqual(1000, order.filled_qty())
        self.assertAlmostEqual(18.4, order.avg_price())
        self.assertEqual(Filled, order.status())

    def test_exec_report_with_diff_ord_id(self):
        order = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="1",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))

        er1 = ModelFactory.build_execution_report(timestamp=0, broker_id="TestBroker",
                                                  broker_event_id="1",
                                                  broker_ord_id="1",
                                                  cl_id='TestClient', cl_ord_id="ERROR", inst_id="HSI@SEHK",
                                                  last_qty=800,
                                                  last_price=18.4,
                                                  status=PartiallyFilled)

        with self.assertRaises(Exception) as ex:
            order.on_exec_report(er1)

    def test_exec_report_with_exceed_qty(self):
        order = Order(ModelFactory.build_order_state_from_nos(
            ModelFactory.build_new_order_request(timestamp=0,
                                                 cl_id='TestClient',
                                                 cl_ord_id="1",
                                                 portf_id="TestPortf",
                                                 broker_id="TestBroker",
                                                 inst_id="HSI@SEHK",
                                                 action=Buy,
                                                 type=Limit,
                                                 qty=1000,
                                                 limit_price=18.5)))

        self.assertEqual(1000, order.leave_qty())
        self.assertEqual(0, len(order.get_events(ExecutionReport)))

        er1 = ModelFactory.build_execution_report(timestamp=0, broker_id="TestBroker",
                                                  broker_event_id="1",
                                                  broker_ord_id="1",
                                                  cl_id='TestClient', cl_ord_id="1", inst_id="HSI@SEHK", last_qty=800,
                                                  last_price=18.4,
                                                  status=PartiallyFilled)
        order.on_exec_report(er1)

        er2 = ModelFactory.build_execution_report(timestamp=0, broker_id="TestBroker",
                                                  broker_event_id="2",
                                                  broker_ord_id="1",
                                                  cl_id='TestClient', cl_ord_id="1", inst_id="HSI@SEHK", last_qty=200,
                                                  last_price=18.4,
                                                  status=Filled)
        order.on_exec_report(er2)

        er3 = ModelFactory.build_execution_report(timestamp=0, broker_id="TestBroker",
                                                  broker_event_id="3",
                                                  broker_ord_id="1",
                                                  cl_id='TestClient', cl_ord_id="1", inst_id="HSI@SEHK", last_qty=100,
                                                  last_price=18.4,
                                                  status=Filled)
        with self.assertRaises(Exception) as ex:
            order.on_exec_report(er3)
