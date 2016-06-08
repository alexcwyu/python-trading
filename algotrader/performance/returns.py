from algotrader.performance import PortfolioAnalyzer
from algotrader.utils.time_series import DataSeries


class Pnl(PortfolioAnalyzer):
    Pnl = "Pnl"

    def __init__(self):
        self.pnl_series = DataSeries(name=Pnl.Pnl)
        self.pnl = 0

    def update(self, time):
        if self.portfolio.total_equity_series.size() >= 2:
            self.pnl = self.portfolio.total_equity_series.get_by_idx(-1) - self.portfolio.total_equity_series.get_by_idx(-2)
            self.pnl_series.add({'timestamp':time, Pnl.Pnl:self.pnl})

    def get_result(self):
        return {Pnl.Pnl: self.pnl}

    def get_series(self):
        return self.pnl_series.get_series(Pnl.Pnl)
