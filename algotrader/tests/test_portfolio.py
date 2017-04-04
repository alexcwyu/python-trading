from collections import defaultdict
from unittest import TestCase

from algotrader.model.model_factory import *
from algotrader.trading.context import ApplicationContext


class PortfolioTest(TestCase):
    def setUp(self):
        self.app_context = ApplicationContext()
        self.app_context.start()
        self.portfolio = self.app_context.portf_mgr.new_portfolio(portf_id="test", initial_cash=100000)
        self.portfolio.start(self.app_context)

    def tearDown(self):
        pass

    def test_portfolio(self):
        self.assertEqual(self.portfolio.state.cash, 100000)

    def test_position(self):
        ord_req1 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='1', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Buy, type=Limit, qty=1000, limit_price=18.5)

        ord_req2 = ModelFactory.build_new_order_request(timestamp=1, cl_id='test', cl_ord_id='2', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Buy, type=Limit, qty=1800, limit_price=18.2)

        self.assertEqual(0, len(self.portfolio.state.positions))
        self.assertEqual(100000, self.portfolio.state.cash)
        self.assertEqual(0, (self.portfolio.performance.now('total_equity')))

        self.portfolio.send_order(ord_req1)
        self.check_order(self.portfolio, [ord_req1], {"HSI@SEHK": (1000, 0)})
        self.assertEqual(100000, self.portfolio.state.cash)
        self.assertEqual(0, (self.portfolio.performance.now("total_equity")))

        self.portfolio.send_order(ord_req2)
        self.check_order(self.portfolio, [ord_req1, ord_req2], {"HSI@SEHK": (2800, 0)})
        self.assertEqual(100000, self.portfolio.state.cash)
        self.assertEqual(0, (self.portfolio.performance.now("total_equity")))

    def test_on_exec_report(self):

        ord_req1 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='1', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Buy, type=Limit, qty=1000, limit_price=18.5)
        order1 = self.portfolio.send_order(ord_req1)

        er1 = ModelFactory.build_execution_report(timestamp=0, cl_id='test', cl_ord_id="1", broker_id="Dummy", broker_event_id="1", broker_ord_id="1", inst_id='HSI@SEHK', last_qty=500, last_price=18.4,
                                                  status=PartiallyFilled)

        self.app_context.order_mgr.on_exec_report(er1)

        self.assertEqual(500, order1.state.last_qty)
        self.assertEqual(18.4, order1.state.last_price)
        self.assertEqual(500, order1.state.filled_qty)
        self.assertEqual(18.4, order1.state.avg_price)
        self.assertEqual(PartiallyFilled, order1.state.status)

        self.check_order(self.portfolio, [ord_req1], {'HSI@SEHK': (1000, 500)})

        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 18.4
        expected_total_equity = expected_cash + expected_stock_value

        self.assertEqual(expected_cash, self.portfolio.state.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance.series.now('stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance.series.now('total_equity'))

        er2 = ModelFactory.build_execution_report(timestamp=0, cl_id='test', cl_ord_id="1", broker_id="Dummy", broker_event_id="2", broker_ord_id="1", inst_id='HSI@SEHK', last_qty=500, last_price=18.2,
                                                  status=Filled)
        self.app_context.order_mgr.on_exec_report(er2)
        self.assertEqual(500, order1.state.last_qty)
        self.assertEqual(18.2, order1.state.last_price)
        self.assertEqual(1000, order1.state.filled_qty)
        self.assertEqual(18.3, order1.state.avg_price)
        self.assertEqual(Filled, order1.state.status)

        self.check_order(self.portfolio, [ord_req1], {'HSI@SEHK': (1000, 1000)})

        expected_cash = 100000 - 500 * 18.4 - 500 * 18.2
        expected_stock_value = 1000 * 18.2
        expected_total_equity = expected_cash + expected_stock_value

        self.assertEqual(expected_cash, self.portfolio.state.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance.series.now('stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance.series.now('total_equity'))

    def test_on_market_date_update(self):

        ord_req1 = ModelFactory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='1', portf_id="test",
                                                        broker_id="Dummy", inst_id='HSI@SEHK',
                                                        action=Buy, type=Limit, qty=1000, limit_price=18.5)

        order1 = self.portfolio.on_new_ord_req(ord_req1)

        er1 = ModelFactory.build_execution_report(timestamp=0, cl_id='test', cl_ord_id="1", broker_id="Dummy", broker_event_id="1", broker_ord_id="1", inst_id='HSI@SEHK', last_qty=500, last_price=18.4,
                                                  status=PartiallyFilled)
        self.app_context.order_mgr.on_exec_report(er1)

        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 18.4
        expected_total_equity = expected_cash + expected_stock_value

        self.assertEqual(expected_cash, self.portfolio.state.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance.series.get_by_idx(0, 'stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance.series.get_by_idx(0, 'total_equity'))

        self.portfolio.on_trade(ModelFactory.build_trade(inst_id='HSI@SEHK', price=20, size=1000, timestamp=2))
        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 20
        expected_total_equity = expected_cash + expected_stock_value
        self.assertEqual(expected_cash, self.portfolio.state.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance.series.get_by_idx(1, 'stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance.series.get_by_idx(1, 'total_equity'))

        self.portfolio.on_bar(ModelFactory.build_bar(inst_id='HSI@SEHK', close=16, adj_close=16, vol=1000, timestamp=3))
        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 16
        expected_total_equity = expected_cash + expected_stock_value
        self.assertEqual(expected_cash, self.portfolio.state.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance.series.get_by_idx(2, 'stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance.series.get_by_idx(2, 'total_equity'))

        self.portfolio.on_quote(ModelFactory.build_quote(inst_id='HSI@SEHK', bid=16, ask=18, timestamp=4))
        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 17
        expected_total_equity = expected_cash + expected_stock_value
        self.assertEqual(expected_cash, self.portfolio.state.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance.series.get_by_idx(3, 'stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance.series.get_by_idx(3, 'total_equity'))


    def check_order(self, portfolio, ord_reqs, qtys):
        # test order requests
        all_ord_reqs = portfolio.ord_reqs.values()
        self.assertEqual(len(ord_reqs), len(all_ord_reqs))
        for ord_req in ord_reqs:
            self.assertTrue(ord_req in all_ord_reqs)

        # test position
        expected_position = defaultdict(list)
        for ord_req in ord_reqs:
            expected_position[ord_req.inst_id].append(ord_req)
        self.assertEqual(len(expected_position), len(portfolio.state.positions))
        for inst_id, pos_ord_reqs in expected_position.items():
            self.assertTrue(portfolio.has_position(inst_id))

            position = portfolio.get_position(inst_id)
            all_position_orders = position.orders
            self.assertEqual(len(pos_ord_reqs), len(all_position_orders))

            (ord_qty, fill_qty) = qtys[inst_id]

            for pos_ord_req in pos_ord_reqs:
                self.assertTrue(ModelFactory.build_cl_ord_id(pos_ord_req.cl_id, pos_ord_req.cl_ord_id) in position.orders)

            self.assertEqual(ord_qty, position.ordered_qty)
            self.assertEqual(fill_qty, position.filled_qty)
