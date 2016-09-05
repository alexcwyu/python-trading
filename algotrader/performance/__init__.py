from algotrader.provider.persistence import Persistable


class PortfolioAnalyzer(Persistable):
    def update(self, time):
        pass

    def get_result(self):
        return None

    def get_series(self):
        return None

    def set_portfolio(self, portfolio):
        self.portfolio = portfolio
