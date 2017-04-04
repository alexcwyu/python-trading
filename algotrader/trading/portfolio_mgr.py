from algotrader import SimpleManager

from algotrader.config.persistence import PersistenceMode
from algotrader.trading.portfolio import Portfolio
from algotrader.model.model_factory import ModelFactory


class PortfolioManager(SimpleManager):
    def __init__(self):
        super(PortfolioManager, self).__init__()

    def _start(self, app_context, **kwargs):
        self.store = self.app_context.get_trade_data_store()
        self.persist_mode = self.app_context.app_config.persistence_config.trade_persist_mode
        self.load_all()

    def load_all(self) -> None:
        if hasattr(self, "store") and self.store:
            self.store.start(self.app_context)
            portfolios = self.store.load_all('portfolios')
            for portfolio in portfolios:
                self.add(portfolio)

    def save_all(self) -> None:
        if hasattr(self, "store") and self.store and self.persist_mode != PersistenceMode.Disable:
            for portfolio in self.all_items():
                self.store.save_portfolio(portfolio)

    def add(self, portfolio: Portfolio) -> None:
        super(PortfolioManager, self).add(portfolio)
        if hasattr(self, "store") and self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_portfolio(portfolio)

    def id(self) -> str:
        return "PortfolioManager"

    def new_portfolio(self, portf_id: str, initial_cash: float = 1000000) -> Portfolio:
        portfolio = Portfolio(ModelFactory.build_portfolio_state(portf_id=portf_id, cash=initial_cash))
        self.add(portfolio)
        return portfolio

    def get_or_new_portfolio(self, portf_id: str, initial_cash: float = 1000000) -> Portfolio:
        if self.has_item(portf_id):
            return self.get(portf_id)
        return self.new_portfolio(portf_id, 1000000)
