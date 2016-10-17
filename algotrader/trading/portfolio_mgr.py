from algotrader import SimpleManager
from algotrader.config.persistence import PersistenceMode
from algotrader.trading.portfolio import Portfolio


class PortfolioManager(SimpleManager):
    def __init__(self):
        super(PortfolioManager, self).__init__()

    def _start(self, app_context, **kwargs):
        self.store = self.app_context.get_trade_data_store()
        self.persist_mode = self.app_context.app_config.persistence_config.trade_persist_mode
        self.load_all()

    def load_all(self):
        if hasattr(self, "store") and self.store:
            self.store.start(self.app_context)
            portfolios = self.store.load_all('portfolios')
            for portfolio in portfolios:
                self.add(portfolio)

    def save_all(self):
        if hasattr(self, "store") and self.store and self.persist_mode != PersistenceMode.Disable:
            for portfolio in self.all_items():
                self.store.save_portfolio(portfolio)

    def add(self, portfolio):
        super(PortfolioManager, self).add(portfolio)
        if hasattr(self, "store") and self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_portfolio(portfolio)

    def id(self):
        return "PortfolioManager"

    def new_portfolio(self, portf_id, cash=1000000, analyzers=None):
        portfolio = Portfolio(portf_id=portf_id, cash=cash, analyzers=analyzers)
        self.add(portfolio)
        return portfolio

    def get_or_new_portfolio(self, portf_id, cash=1000000, analyzers=None):
        if self.has_item(portf_id):
            return self.get(portf_id)
        return self.new_portfolio(portf_id, 1000000, analyzers)
