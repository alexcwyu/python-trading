from algotrader import SimpleManager


class PortfolioManager(SimpleManager):
    def __init__(self, app_context=None):
        super(SimpleManager, self).__init__()
        self.app_context = app_context

    def _start(self):
        self.store = self.app_context.get_trade_data_store()
        self._load_all()

    def _load_all(self):
        if self.store:
            portfolios = self.store.load_all('portfolios')
            for portfolio in portfolios:
                self.add(portfolio)

    def _save_all(self):
        if self.store:
            for portfolio in self.all_portfolios():
                self.store.save_portfolio(portfolio)


portf_mgr = PortfolioManager()
