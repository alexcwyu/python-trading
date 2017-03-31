from algotrader.trading.analyzer import Analyzer
from algotrader.trading.data_series import DataSeries

from algotrader.trading.analyzer.performance import PerformanceAnalyzer


class PnlAnalyzer(Analyzer):
    Pnl = "Pnl"

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.state = portfolio.state.pnl
        self.series = DataSeries(self.portfolio.state.pnl.series)

    def update(self, timestamp: int, total_equity: float):
        performance_series = self.portfolio.performance.series

        if self.series.size() >= 2:
            self.state.pnl = performance_series.get_by_idx(-1, PerformanceAnalyzer.TotalEquity) - \
                             self.portfolio.performance_series.get_by_idx(-2, PerformanceAnalyzer.TotalEquity)

            self.series.add(data={self.Pnl: self.state.pnl}, timestamp=timestamp)

    def get_result(self):
        return {self.Pnl: self.state.pnl}

    def get_series(self, keys=None):
        keys = keys if keys else self.Pnl
        return {self.Pnl: self.series.get_series(self.Pnl)}
