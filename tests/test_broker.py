from unittest import TestCase

from algotrader.trading.event import ExecutionEventHandler
from algotrader.model.model_factory import ModelFactory
from algotrader.model.trade_data_pb2 import *
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.trading.context import ApplicationContext
from tests import empty_config


class SimulatorTest(TestCase):
    class ExecHandler(ExecutionEventHandler):
        def __init__(self):
            self.ord_upds = list()
            self.exec_reports = list()

        def on_ord_upd(self, ord_upd):
            self.ord_upds.append(ord_upd)

        def on_exec_report(self, exec_report):
            self.exec_reports.append(exec_report)

        def reset(self):
            self.ord_upds = list()
            self.exec_reports = list()

        def id(self):
            return "ExecHandler"

    def setUp(self):
        self.app_context = ApplicationContext()
        # self.app_context.inst_data_mgr.clear()

        self.exec_handler = SimulatorTest.ExecHandler()
        self.app_context.order_mgr = self.exec_handler
        self.simulator = Simulator()
        self.simulator.start(app_context=self.app_context)

    def test_on_limit_order_fill_with_new_data(self):
        orders = self.simulator._get_orders()
        self.assertEqual(0, len(orders))

        nos = ModelFactory.build_new_order_request(timestamp=0,
                                                   cl_id='TestClient', cl_ord_id="TestClientOrder",
                                                   portf_id="TestPortf", broker_id="TestBroker",
                                                   inst_id="HSI@SEHK", action=Buy, type=Limit, qty=1000,
                                                   limit_price=18.5)
        self.simulator.on_new_ord_req(nos)
        cl_ord_id = ModelFactory.build_cl_ord_id(nos.cl_id, nos.cl_ord_id)
        orders = self.simulator._get_orders()
        self.assertEqual(1, len(orders))
        self.assertEqual(1, len(orders[nos.inst_id]))
        self.assertIsNotNone(orders[nos.inst_id][cl_ord_id])
        self.assertEqual(1, len(self.exec_handler.exec_reports))

        exec_report = self.exec_handler.exec_reports[0]
        self.assert_exec_report(exec_report, nos.cl_id, nos.cl_ord_id, 0, 0, Submitted)

        bar1 = ModelFactory.build_bar(timestamp=0, inst_id="HSI@SEHK", open=20, high=21, low=19, close=20.5, vol=1000)
        bar2 = ModelFactory.build_bar(timestamp=1, inst_id="HSI@SEHK", open=16, high=18, low=15, close=17, vol=1000)

        self.exec_handler.reset()
        self.simulator.on_bar(bar1)
        self.assertEqual(0, len(self.exec_handler.exec_reports))

        self.exec_handler.reset()
        self.simulator.on_bar(bar2)
        self.assertEqual(1, len(self.exec_handler.exec_reports))
        exec_report = self.exec_handler.exec_reports[0]
        self.assert_exec_report(exec_report, nos.cl_id, nos.cl_ord_id, 1000, 18.5, Filled)

    def test_on_limit_order_immediate_fill(self):
        # bar1 = Bar(inst_id=1, open=20, high=21, low=19, close=20.5, vol=1000)
        bar2 = ModelFactory.build_bar(timestamp=1, inst_id="HSI@SEHK", open=16, high=18, low=15, close=17, vol=1000)

        self.app_context.inst_data_mgr.on_bar(bar2)

        orders = self.simulator._get_orders()
        self.assertEqual(0, len(orders))

        nos = ModelFactory.build_new_order_request(timestamp=0,
                                                   cl_id='TestClient', cl_ord_id="TestClientOrder",
                                                   portf_id="TestPortf", broker_id="TestBroker",
                                                   inst_id="HSI@SEHK", action=Buy, type=Limit, qty=1000,
                                                   limit_price=18.5)

        self.simulator.on_new_ord_req(nos)

        cl_ord_id = ModelFactory.build_cl_ord_id(nos.cl_id, nos.cl_ord_id)
        orders = self.simulator._get_orders()
        self.assertEqual(1, len(orders))
        self.assertEqual(0, len(orders[nos.inst_id]))

        self.assertEqual(2, len(self.exec_handler.exec_reports))

        exec_report = self.exec_handler.exec_reports[0]
        self.assert_exec_report(exec_report, nos.cl_id, nos.cl_ord_id, 0, 0, Submitted)

        exec_report = self.exec_handler.exec_reports[1]
        self.assert_exec_report(exec_report, nos.cl_id, nos.cl_ord_id, 1000, 18.5, Filled)

    def assert_exec_report(self, exec_report, cl_id, cl_ord_id, last_qty, last_price, status):
        self.assertEqual(cl_id, exec_report.cl_id)
        self.assertEqual(cl_ord_id, exec_report.cl_ord_id)
        self.assertEqual(last_qty, exec_report.last_qty)
        self.assertEqual(last_price, exec_report.last_price)
        self.assertEqual(status, exec_report.status)
