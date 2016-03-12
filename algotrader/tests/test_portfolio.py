from algotrader.trading.portfolio import Portfolio
from algotrader.event.order import *
from unittest import TestCase
from collections import defaultdict

class TestPortfolio(TestCase):
    def test_on_order(self):
        portfolio = Portfolio()
        self.assertEqual(portfolio.cash, 100000)

        order1 = Order(ord_id=1, instrument="HSI",action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        order2 = Order(ord_id=2, instrument="HSI",action=OrdAction.BUY, type=OrdType.LIMIT, qty=1800, limit_price=18.2)

        self.assertEqual(0, len(portfolio.positions))

        portfolio.on_order(order1)
        self.check_order(portfolio, [order1])

        # position = positions['HSI']
        #
        # self.assertEqual(1, len(portfolio.positions))
        # self.assertEqual(1, len(portfolio.orders))
        # self.assertTrue(order1 in portfolio.orders.values())
        #
        # self.assertEqual(1, len(position.orders))
        # self.assertTrue(order1 in position.orders.values())


        portfolio.on_order(order2)
        self.check_order(portfolio, [order1, order2])

        # self.assertEqual(1, len(portfolio.positions))
        # self.assertEqual(2, len(portfolio.orders))
        # self.assertTrue(order1 in portfolio.orders.values())
        # self.assertTrue(order2 in portfolio.orders.values())
        #
        # self.assertEqual(2, len(position.orders))
        # self.assertTrue(order1 in position.orders.values())
        # self.assertTrue(order2 in position.orders.values())


        positions = portfolio.positions
        print positions


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

            ord_qty, fill_qty = qtys[inst]

            for pos_order in pos_orders:
                self.assertTrue(pos_order in position.orders.values())


