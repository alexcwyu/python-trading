from algotrader.trading.portfolio import Portfolio
from algotrader.event.order import *
from unittest import TestCase

class TestPortfolio(TestCase):
    def test_on_order(self):
        portfolio = Portfolio()
        self.assertEqual(portfolio.cash, 100000)

        order = Order(ord_id=1, instrument="HSI",action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)
        print order

        portfolio.on_order(order)

        positions = portfolio.positions

        print positions