from algotrader.analyzer import Analyzer

from algotrader.analyzer.performance import PerformanceAnalyzer
from algotrader.trading.data_series import DataSeries


class PnlAnalyzer(Analyzer):
    Pnl = "Pnl"

    def __init__(self, portfolio, state):
        self.portfolio = portfolio
        self.state = state
        self.series = DataSeries(time_series=self.state.pnl.series)

    def update(self, timestamp: int, total_equity: float):
        performance_series = self.portfolio.performance.series

        if self.series.size() >= 2:
            self.state.pnl.last_pnl = performance_series.get_by_idx(-1, PerformanceAnalyzer.TotalEquity) - \
                                      performance_series.get_by_idx(-2, PerformanceAnalyzer.TotalEquity)

            self.series.add(timestamp=timestamp, data={self.Pnl: self.state.pnl.last_pnl})
        else:
            self.state.pnl.last_pnl = 0
            self.series.add(timestamp=timestamp, data={self.Pnl: self.state.pnl.last_pnl})

    def get_result(self):
        return {self.Pnl: self.state.pnl.last_pnl}

    def get_series(self, keys=None):
        keys = keys if keys else self.Pnl
        return {self.Pnl: self.series.get_series(self.Pnl)}

    def last_pnl(self) -> float:
        return self.state.pnl.last_pnl
