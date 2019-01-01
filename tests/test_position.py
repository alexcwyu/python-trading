from unittest import TestCase

from algotrader.model.model_factory import *
from algotrader.trading.context import ApplicationContext


class PositionTest(TestCase):
    def setUp(self):
        self.app_context = ApplicationContext()
        self.app_context.start()
        self.portfolio = self.app_context.portf_mgr.new_portfolio(portf_id="test", initial_cash=100000)
        self.portfolio.start(self.app_context)

    def test_add_order(self):
        self.assertEquals(0, self.portfolio.position_filled_qty("HSI@SEHK"))
        self.assertEquals(0, len(self.portfolio.position_order_ids("HSI@SEHK")))

        ord_req1 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='1', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Buy, type=Limit, qty=1000, limit_price=18.5)
        self.portfolio.send_order(ord_req1)

        self.assertEquals(1000, self.portfolio.position_ordered_qty("HSI@SEHK"))
        self.assertEquals(1, len(self.portfolio.position_order_ids("HSI@SEHK")))

        ord_req2 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='2', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Buy, type=Limit, qty=1000, limit_price=18.5)

        self.portfolio.send_order(ord_req2)

        self.assertEquals(2000, self.portfolio.position_ordered_qty("HSI@SEHK"))
        self.assertEquals(2, len(self.portfolio.position_order_ids("HSI@SEHK")))

        ord_req3 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='3', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Sell, type=Limit, qty=1200, limit_price=18.5)

        self.portfolio.send_order(ord_req3)

        self.assertEquals(800, self.portfolio.position_ordered_qty("HSI@SEHK"))
        self.assertEquals(3, len(self.portfolio.position_order_ids("HSI@SEHK")))

    def test_add_order_with_same_ord_id(self):
        ord_req1 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='1', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Buy, type=Limit, qty=1000, limit_price=18.5)
        self.portfolio.send_order(ord_req1)

        with self.assertRaises(Exception) as ex:
            self.portfolio.send_order(ord_req1)

    def test_fill_qty(self):
        self.assertEquals(0, self.portfolio.position_filled_qty("HSI@SEHK"))

        ord_req1 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='1', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Buy, type=Limit, qty=1000, limit_price=18.5)
        self.portfolio.send_order(ord_req1)
        self.assertEquals(0, self.portfolio.position_filled_qty("HSI@SEHK"))

        er1 = ModelFactory.build_execution_report(timestamp=0, cl_id='test', cl_ord_id="1", broker_id="Dummy",
                                                  broker_event_id="1", broker_ord_id="1", inst_id='HSI@SEHK',
                                                  last_qty=500, last_price=18.4,
                                                  status=PartiallyFilled)
        self.portfolio.on_exec_report(er1)
        self.assertEquals(500, self.portfolio.position_filled_qty("HSI@SEHK"))

        er2 = ModelFactory.build_execution_report(timestamp=0, cl_id='test', cl_ord_id="1", broker_id="Dummy",
                                                  broker_event_id="2", broker_ord_id="1", inst_id='HSI@SEHK',
                                                  last_qty=500, last_price=18.4,
                                                  status=Filled)
        self.portfolio.on_exec_report(er2)
        self.assertEquals(1000, self.portfolio.position_filled_qty("HSI@SEHK"))

        ord_req2 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='2', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Sell, type=Limit, qty=1200, limit_price=18.5)
        self.portfolio.send_order(ord_req2)
        self.assertEquals(1000, self.portfolio.position_filled_qty("HSI@SEHK"))

        er3 = ModelFactory.build_execution_report(timestamp=0, cl_id='test', cl_ord_id="2", broker_id="Dummy",
                                                  broker_event_id="3", broker_ord_id="2", inst_id='HSI@SEHK',
                                                  last_qty=800, last_price=18.4,
                                                  status=PartiallyFilled)

        self.portfolio.on_exec_report(er3)
        self.assertEquals(200, self.portfolio.position_filled_qty("HSI@SEHK"))

        er4 = ModelFactory.build_execution_report(timestamp=0, cl_id='test', cl_ord_id="2", broker_id="Dummy",
                                                  broker_event_id="3", broker_ord_id="2", inst_id='HSI@SEHK',
                                                  last_qty=400, last_price=18.4,
                                                  status=Filled)

        self.portfolio.on_exec_report(er4)
        self.assertEquals(-200, self.portfolio.position_filled_qty("HSI@SEHK"))

    def test_fill_qty_with_diff_inst(self):
        ord_req1 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='1', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Buy, type=Limit, qty=1000, limit_price=18.5)
        self.portfolio.send_order(ord_req1)

        ord_req2 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='2', portf_id="test",
                                                        broker_id="Dummy", inst_id='0005.HK@SEHK',
                                                        action=Sell, type=Limit, qty=800, limit_price=80)
        self.portfolio.send_order(ord_req2)

        self.assertEquals(0, self.portfolio.position_filled_qty("HSI@SEHK"))
        self.assertEquals(1000, self.portfolio.position_ordered_qty("HSI@SEHK"))
        self.assertEquals(0, self.portfolio.position_filled_qty("0005.HK@SEHK"))
        self.assertEquals(-800, self.portfolio.position_ordered_qty("0005.HK@SEHK"))

        er1 = ModelFactory.build_execution_report(timestamp=0, cl_id='test', cl_ord_id="1", broker_id="Dummy",
                                                  broker_event_id="1", broker_ord_id="1", inst_id='HSI@SEHK',
                                                  last_qty=500, last_price=18.4,
                                                  status=PartiallyFilled)
        self.portfolio.on_exec_report(er1)

        self.assertEquals(500, self.portfolio.position_filled_qty("HSI@SEHK"))
        self.assertEquals(1000, self.portfolio.position_ordered_qty("HSI@SEHK"))
        self.assertEquals(0, self.portfolio.position_filled_qty("0005.HK@SEHK"))
        self.assertEquals(-800, self.portfolio.position_ordered_qty("0005.HK@SEHK"))

        er2 = ModelFactory.build_execution_report(timestamp=0, cl_id='test', cl_ord_id="2", broker_id="Dummy",
                                                  broker_event_id="2", broker_ord_id="2", inst_id='0005.HK@SEHK',
                                                  last_qty=600, last_price=80,
                                                  status=PartiallyFilled)
        self.portfolio.on_exec_report(er2)

        self.assertEquals(500, self.portfolio.position_filled_qty("HSI@SEHK"))
        self.assertEquals(1000, self.portfolio.position_ordered_qty("HSI@SEHK"))
        self.assertEquals(-600, self.portfolio.position_filled_qty("0005.HK@SEHK"))
        self.assertEquals(-800, self.portfolio.position_ordered_qty("0005.HK@SEHK"))
