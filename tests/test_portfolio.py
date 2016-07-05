import math
from collections import defaultdict
from unittest import TestCase

from algotrader.event.market_data import Trade, Bar, Quote
from algotrader.event.order import Order, OrdAction, OrdType, NewOrderRequest, OrdStatus, OrderStatusUpdate, ExecutionReport
from algotrader.trading.portfolio import Portfolio
from algotrader.trading.order_mgr import order_mgr


class PortfolioTest(TestCase):
    def setUp(self):
        self.portfolio = Portfolio(cash=100000)
        order_mgr.reset()

    def test_portfolio(self):
        self.assertEqual(Portfolio(cash=100000).cash, 100000)

    def test_position(self):

        ord_req1 = NewOrderRequest(cl_id='test', cl_ord_id=1, portf_id="test", broker_id ="Dummy", inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        ord_req2 = NewOrderRequest(cl_id='test', cl_ord_id=2, portf_id="test", broker_id ="Dummy", inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1800, limit_price=18.2)

        self.assertEqual(0, len(self.portfolio.positions))
        self.assertEqual(100000, self.portfolio.cash)
        self.assertTrue(math.isnan(self.portfolio.performance_series.now("total_equity")))

        order1 = self.portfolio.send_order(ord_req1)
        self.check_order(self.portfolio, [order1], {1: (1000, 0)})
        self.assertEqual(100000, self.portfolio.cash)
        self.assertTrue(math.isnan(self.portfolio.performance_series.now("total_equity")))

        order2 = self.portfolio.send_order(ord_req2)
        self.check_order(self.portfolio, [order1, order2], {1: (2800, 0)})
        self.assertEqual(100000, self.portfolio.cash)
        self.assertTrue(math.isnan(self.portfolio.performance_series.now("total_equity")))

    def test_on_exec_report(self):

        ord_req = NewOrderRequest(cl_id='test', cl_ord_id=1, portf_id="test", broker_id ="Dummy", inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        order1 = self.portfolio.send_order(ord_req)

        er1 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=1, inst_id=1, last_qty=500, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)

        order_mgr.on_exec_report(er1)

        self.assertEqual(500, order1.last_qty)
        self.assertEqual(18.4, order1.last_price)
        self.assertEqual(500, order1.filled_qty)
        self.assertEqual(18.4, order1.avg_price)
        self.assertEqual(OrdStatus.PARTIALLY_FILLED, order1.status)

        self.check_order(self.portfolio, [order1], {1: (1000, 500)})

        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 18.4
        expected_total_equity = expected_cash + expected_stock_value

        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance_series.now('stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance_series.now('total_equity'))

        er2 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=2, inst_id=1, last_qty=500, last_price=18.2,
                              status=OrdStatus.FILLED)
        order_mgr.on_exec_report(er2)
        self.assertEqual(500, order1.last_qty)
        self.assertEqual(18.2, order1.last_price)
        self.assertEqual(1000, order1.filled_qty)
        self.assertEqual(18.3, order1.avg_price)
        self.assertEqual(OrdStatus.FILLED, order1.status)

        self.check_order(self.portfolio, [order1], {1: (1000, 1000)})

        expected_cash = 100000 - 500 * 18.4 - 500 * 18.2
        expected_stock_value = 1000 * 18.2
        expected_total_equity = expected_cash + expected_stock_value

        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance_series.now('stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance_series.now('total_equity'))

    def test_on_market_date_update(self):

        ord_req = NewOrderRequest(cl_id='test', cl_ord_id=1, portf_id="test", broker_id ="Dummy", inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5,
                                timestamp=0)
        order1 = self.portfolio.on_new_ord_req(ord_req)

        er1 = ExecutionReport(cl_id='test', cl_ord_id=1, ord_id=1, er_id=1, inst_id=1, last_qty=500, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED, timestamp=1)
        order_mgr.on_exec_report(er1)

        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 18.4
        expected_total_equity = expected_cash + expected_stock_value

        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance_series.get_by_idx(0, 'stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance_series.get_by_idx(0, 'total_equity'))

        self.portfolio.on_trade(Trade(inst_id=1, price=20, size=1000, timestamp=2))
        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 20
        expected_total_equity = expected_cash + expected_stock_value
        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance_series.get_by_idx(1, 'stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance_series.get_by_idx(1, 'total_equity'))

        self.portfolio.on_bar(Bar(inst_id=1, close=16, adj_close=16, vol=1000, timestamp=3))
        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 16
        expected_total_equity = expected_cash + expected_stock_value
        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance_series.get_by_idx(2, 'stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance_series.get_by_idx(2, 'total_equity'))

        self.portfolio.on_quote(Quote(inst_id=1, bid=16, ask=18, timestamp=4))
        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 17
        expected_total_equity = expected_cash + expected_stock_value
        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.performance_series.get_by_idx(3, 'stock_value'))
        self.assertEqual(expected_total_equity, self.portfolio.performance_series.get_by_idx(3, 'total_equity'))

    def check_order(self, portfolio, orders, qtys):
        expected_positon = defaultdict(list)
        for order in orders:
            expected_positon[order.inst_id].append(order)

        self.assertEqual(len(expected_positon), len(portfolio.positions))

        all_orders = portfolio.all_orders()
        self.assertEqual(len(orders), len(all_orders))

        for order in orders:
            self.assertTrue(order in all_orders)

        for inst, pos_orders in expected_positon.iteritems():
            position = portfolio.positions[inst]

            all_position_orders = position.all_orders()
            self.assertEqual(len(pos_orders), len(all_position_orders))

            (ord_qty, fill_qty) = qtys[inst]

            for pos_order in pos_orders:
                self.assertEquals(pos_order, position.orders[pos_order.cl_id][pos_order.cl_ord_id])

            self.assertEqual(ord_qty, position.ordered_size)
            self.assertEqual(fill_qty, position.total_qty())
