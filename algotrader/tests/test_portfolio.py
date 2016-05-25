import math
from collections import defaultdict
from unittest import TestCase

from algotrader.event.order import *
from algotrader.trading.portfolio import Portfolio


class TestPortfolio(TestCase):
    def setUp(self):
        self.portfolio = Portfolio(cash=100000)

    def test_portfolio(self):
        self.assertEqual(self.portfolio.cash, 100000)

    def test_position(self):

        order1 = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        order2 = Order(ord_id=2, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1800, limit_price=18.2)

        self.assertEqual(0, len(self.portfolio.positions))
        self.assertEqual(100000, self.portfolio.cash)
        self.assertTrue(math.isnan(self.portfolio.total_equity_series.now()))

        self.portfolio.on_order(order1)
        self.check_order(self.portfolio, [order1], {'HSI': (1000, 0)})
        self.assertEqual(100000, self.portfolio.cash)
        self.assertTrue(math.isnan(self.portfolio.total_equity_series.now()))

        self.portfolio.on_order(order2)
        self.check_order(self.portfolio, [order1, order2], {'HSI': (2800, 0)})
        self.assertEqual(100000, self.portfolio.cash)
        self.assertTrue(math.isnan(self.portfolio.total_equity_series.now()))

    def test_on_ord_update(self):

        order1 = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        self.portfolio.on_order(order1)

        status_update = OrderStatusUpdate(ord_id=1, instrument="HSI", status=OrdStatus.NEW)
        self.portfolio.on_ord_upd(status_update)
        self.assertEqual(OrdStatus.NEW, order1.status)

    def test_on_exec_report(self):

        order1 = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        self.portfolio.on_order(order1)

        er1 = ExecutionReport(ord_id=1, er_id=1, instrument="HSI", last_qty=500, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        self.portfolio.on_exec_report(er1)
        self.assertEqual(500, order1.last_qty)
        self.assertEqual(18.4, order1.last_price)
        self.assertEqual(500, order1.filled_qty)
        self.assertEqual(18.4, order1.avg_price)
        self.assertEqual(OrdStatus.PARTIALLY_FILLED, order1.status)

        self.check_order(self.portfolio, [order1], {'HSI': (1000, 500)})

        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 18.4
        expected_total_equity = expected_cash + expected_stock_value

        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.stock_value_series.now())
        self.assertEqual(expected_total_equity, self.portfolio.total_equity_series.now())

        er2 = ExecutionReport(ord_id=1, er_id=2, instrument="HSI", last_qty=500, last_price=18.2,
                              status=OrdStatus.FILLED)
        self.portfolio.on_exec_report(er2)
        self.assertEqual(500, order1.last_qty)
        self.assertEqual(18.2, order1.last_price)
        self.assertEqual(1000, order1.filled_qty)
        self.assertEqual(18.3, order1.avg_price)
        self.assertEqual(OrdStatus.FILLED, order1.status)

        self.check_order(self.portfolio, [order1], {'HSI': (1000, 1000)})

        expected_cash = 100000 - 500 * 18.4 - 500 * 18.2
        expected_stock_value = 1000 * 18.2
        expected_total_equity = expected_cash + expected_stock_value

        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.stock_value_series.now())
        self.assertEqual(expected_total_equity, self.portfolio.total_equity_series.now())

    def test_on_market_date_update(self):

        order1 = Order(ord_id=1, instrument="HSI", action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        self.portfolio.on_order(order1)

        er1 = ExecutionReport(ord_id=1, er_id=1, instrument="HSI", last_qty=500, last_price=18.4,
                              status=OrdStatus.PARTIALLY_FILLED)
        self.portfolio.on_exec_report(er1)

        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 18.4
        expected_total_equity = expected_cash + expected_stock_value

        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.stock_value_series.get_by_idx(0))
        self.assertEqual(expected_total_equity, self.portfolio.total_equity_series.get_by_idx(0))

        self.portfolio.on_trade(Trade(instrument='HSI', price=20, size=1000))
        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 20
        expected_total_equity = expected_cash + expected_stock_value
        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.stock_value_series.get_by_idx(1))
        self.assertEqual(expected_total_equity, self.portfolio.total_equity_series.get_by_idx(1))

        self.portfolio.on_bar(Bar(instrument='HSI', close=16, adj_close=16, vol=1000))
        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 16
        expected_total_equity = expected_cash + expected_stock_value
        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.stock_value_series.get_by_idx(2))
        self.assertEqual(expected_total_equity, self.portfolio.total_equity_series.get_by_idx(2))

        self.portfolio.on_quote(Quote(instrument='HSI', bid=16, ask=18))
        expected_cash = 100000 - 500 * 18.4
        expected_stock_value = 500 * 17
        expected_total_equity = expected_cash + expected_stock_value
        self.assertEqual(expected_cash, self.portfolio.cash)
        self.assertEqual(expected_stock_value, self.portfolio.stock_value_series.get_by_idx(3))
        self.assertEqual(expected_total_equity, self.portfolio.total_equity_series.get_by_idx(3))

    def check_order(self, portfolio, orders, qtys):
        expected_positon = defaultdict(list)
        for order in orders:
            expected_positon[order.instrument].append(order)

        self.assertEqual(len(expected_positon), len(portfolio.positions))
        self.assertEqual(len(orders), len(portfolio.orders))

        for order in orders:
            self.assertTrue(order in portfolio.orders.values())

        for inst, pos_orders in expected_positon.iteritems():
            position = portfolio.positions[inst]

            self.assertEqual(len(pos_orders), len(position.orders))

            (ord_qty, fill_qty) = qtys[inst]

            for pos_order in pos_orders:
                self.assertTrue(pos_order in position.orders.values())

            self.assertEqual(ord_qty, position.size)
            self.assertEqual(fill_qty, position.filled_qty())
