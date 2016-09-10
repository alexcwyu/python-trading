from algotrader import SimpleManager
from algotrader.trading.portfolio import Portfolio


class PortfolioManager(SimpleManager):
    def __init__(self):
        super(PortfolioManager, self).__init__()

    def _start(self, app_context, **kwargs):
        self.store = self.app_context.get_trade_data_store()
        self.load_all()

    def load_all(self):
        if self.store:
            portfolios = self.store.load_all('portfolios')
            for portfolio in portfolios:
                self.add(portfolio)

    def save_all(self):
        if self.store:
            for portfolio in self.all_items():
                self.store.save_portfolio(portfolio)

    def id(self):
        return "PortfolioManager"

    def new_portfolio(self, portf_id, cash=1000000, analyzers=None):
        portfolio = Portfolio(portf_id=portf_id, cash=cash, analyzers=analyzers)
        self.add(portfolio)
        return portfolio
