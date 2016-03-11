from algotrader.trading.portfolio import Portfolio
from algotrader.event.order import *
from unittest import TestCase

class TestPortfolio(TestCase):
    def test_on_order(self):
        portfolio = Portfolio()
        self.assertEqual(portfolio.cash, 100000)

        order = Order