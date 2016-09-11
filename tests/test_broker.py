from unittest import TestCase

from algotrader.config.app import ApplicationConfig
from algotrader.event.event_handler import ExecutionEventHandler
from algotrader.event.market_data import Bar
from algotrader.event.order import NewOrderRequest, OrdStatus, OrdAction, OrdType
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.trading.context import ApplicationContext


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
        self.app_config = ApplicationConfig(None, None, None, None, None, None, None)
        self.app_context = ApplicationContext(app_config=self.app_config)
        #self.app_context.inst_data_mgr.clear()

        self.exec_handler = SimulatorTest.ExecHandler()
        self.app_context.order_mgr = self.exec_handler
        self.simulator = Simulator()
        self.simulator.start(app_context=self.app_context)

    def test_on_limit_order_fill_with_new_data(self):
        orders = self.simulator._get_orders()
        self.assertEqual(0, len(orders))

        order1 = NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT,
                                 qty=1000, limit_price=18.5)
        self.simulator.on_new_ord_req(order1)

        orders = self.simulator._get_orders()
        self.assertEqual(1, len(orders))
        self.assertEqual(1, len(orders[order1.inst_id]))
        self.assertEqual(1, len(orders[order1.inst_id][order1.cl_id]))
        self.assertIsNotNone(orders[order1.inst_id][order1.cl_id][order1.cl_ord_id])
        self.assertEqual(1, len(self.exec_handler.exec_reports))

        exec_report = self.exec_handler.exec_reports[0]
        self.assert_exec_report(exec_report, order1.cl_id, order1.cl_ord_id, 0, 0, OrdStatus.SUBMITTED)

        bar1 = Bar(inst_id=1, open=20, high=21, low=19, close=20.5, vol=1000)
        bar2 = Bar(inst_id=1, open=16, high=18, low=15, close=17, vol=1000)

        self.exec_handler.reset()
        self.simulator.on_bar(bar1)
        self.assertEqual(0, len(self.exec_handler.exec_reports))

        self.exec_handler.reset()
        self.simulator.on_bar(bar2)
        self.assertEqual(1, len(self.exec_handler.exec_reports))
        exec_report = self.exec_handler.exec_reports[0]
        self.assert_exec_report(exec_report, order1.cl_id, order1.cl_ord_id, 1000, 18.5, OrdStatus.FILLED)

    def test_on_limit_order_immediate_fill(self):
        bar1 = Bar(inst_id=1, open=20, high=21, low=19, close=20.5, vol=1000)
        bar2 = Bar(inst_id=1, open=16, high=18, low=15, close=17, vol=1000)

        self.app_context.inst_data_mgr.on_bar(bar2)

        orders = self.simulator._get_orders()
        self.assertEqual(0, len(orders))

        order1 = NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT,
                                 qty=1000, limit_price=18.5)
        self.simulator.on_new_ord_req(order1)

        orders = self.simulator._get_orders()
        self.assertEqual(1, len(orders))
        self.assertEqual(1, len(orders[order1.inst_id]))
        self.assertEqual(0, len(orders[order1.inst_id][order1.cl_id]))

        self.assertEqual(2, len(self.exec_handler.exec_reports))

        exec_report = self.exec_handler.exec_reports[0]
        self.assert_exec_report(exec_report, order1.cl_id, order1.cl_ord_id, 0, 0, OrdStatus.SUBMITTED)

        exec_report = self.exec_handler.exec_reports[1]
        self.assert_exec_report(exec_report, order1.cl_id, order1.cl_ord_id, 1000, 18.5, OrdStatus.FILLED)

    def assert_exec_report(self, exec_report, cl_id, cl_ord_id, last_qty, last_price, status):
        self.assertEqual(cl_id, exec_report.cl_id)
        self.assertEqual(cl_ord_id, exec_report.cl_ord_id)
        self.assertEqual(last_qty, exec_report.last_qty)
        self.assertEqual(last_price, exec_report.last_price)
        self.assertEqual(status, exec_report.status)
