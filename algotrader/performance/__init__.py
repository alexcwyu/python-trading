from algotrader.provider.persistence import Persistable


class PortfolioAnalyzer(Persistable):
    __slots__ = (
        'portfolio', #TODO: review this, portfolio is belongs to slots and transient at the same time?
    )

    __transient__ = (
        'portfolio',
    )

    def __init__(self):
        self.portfolio = None

    def update(self, time):
        pass

    def get_result(self):
        return None

    def get_series(self):
        return None

    def set_portfolio(self, portfolio):
        self.portfolio = portfolio
