from collections import defaultdict
from unittest import TestCase

from algotrader.event.order import OrdAction, OrdType
from algotrader.model.model_factory import ModelFactory
from algotrader.model.trading.portfolio import Portfolio


class PortfolioTest(TestCase):
    factory = ModelFactory()

    def setUp(self):
        self.portfolio = Portfolio(PortfolioTest.factory.build_portfolio_state(portf_id="test", cash=100000),PortfolioTest.factory)

    def tearDown(self):
        pass

    def test_portfolio(self):
        self.assertEqual(self.portfolio.state.cash, 100000)


    def test_position(self):
        ord_req1 = PortfolioTest.factory.build_new_order_request(timestamp=0, cl_id='test', cl_ord_id='1', portf_id="test", broker_id="Dummy", inst_id='HSI@SEHK',
                                   action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000, limit_price=18.5)


        ord_req2 = PortfolioTest.factory.build_new_order_request(timestamp=1, cl_id='test', cl_ord_id='2', portf_id="test", broker_id="Dummy", inst_id='HSI@SEHK',
                                   action=OrdAction.BUY, type=OrdType.LIMIT, qty=1800, limit_price=18.2)

        self.assertEqual(0, len(self.portfolio.state.positions))
        self.assertEqual(100000, self.portfolio.state.cash)
        self.assertEqual(0, (self.portfolio.performance.now('total_equity')))


        order1 = self.portfolio.send_order(ord_req1)
        #self.check_order(self.portfolio, [order1], {1: (1000, 0)})
        self.assertEqual(100000, self.portfolio.state.cash)
        self.assertEqual(0, (self.portfolio.performance.now("total_equity")))

        order2 = self.portfolio.send_order(ord_req2)
        #self.check_order(self.portfolio, [order1, order2], {1: (2800, 0)})
        self.assertEqual(100000, self.portfolio.state.cash)
        self.assertEqual(0, (self.portfolio.performance.now("total_equity")))



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
            position = portfolio.positions[str(inst)]

            all_position_orders = position.all_orders()
            self.assertEqual(len(pos_orders), len(all_position_orders))

            (ord_qty, fill_qty) = qtys[inst]

            for pos_order in pos_orders:
                self.assertEquals(pos_order, position.orders[pos_order.cl_id][pos_order.cl_ord_id])

            self.assertEqual(ord_qty, position.ordered_qty())
            self.assertEqual(fill_qty, position.filled_qty())
