from collections import defaultdict
from unittest import TestCase

from algotrader.event.market_data import Trade, Bar, Quote
from algotrader.model.trading.portfolio import Portfolio
from algotrader.model.model_factory import ModelFactory

class PortfolioTest(TestCase):
    def setUp(self):
        factory = ModelFactory()
        self.portfolio = Portfolio(factory.build_portfolio_state(portf_id="test", cash=89))

    def tearDown(self):
        pass

    def test_portfolio(self):
        self.assertEqual(self.portfolio.state.cash, 89)