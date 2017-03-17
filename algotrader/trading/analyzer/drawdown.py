from algotrader.trading.analyzer import Analyzer
from algotrader.trading.data_series import DataSeries


class DrawDownAnalyzer(Analyzer):
    DrawDown = "DrawDown"
    DrawDownPct = "DrawDown%"
    HighEquity = "HighEquity"
    LowEquity = "LowEquity"
    CurrentRunUp = "CurrentRunUp"
    CurrentDrawDown = "CurrentDrawDown"

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.state = self.portfolio.state.drawdown
        self.series = DataSeries(self.state.series)

    def update(self, timestamp: int, current_value: float):
        total_equity = self.portfolio.total_equity
        if self.portfolio.performance_series.size() == 1:
            self.state.low_equity = total_equity
            self.state.high_equity = total_equity
        else:
            if total_equity > self.state.high_equity:
                self.state.high_equity = total_equity
                self.state.low_equity = total_equity
                self.state.current_drawdown = 0
            elif total_equity < self.state.low_equity:
                self.state.low_equity = total_equity
                self.state.current_run_up = 0
            elif total_equity > self.state.low_equity and total_equity < self.state.high_equity:
                self.state.current_drawdown = 1 - total_equity / self.state.high_equity
                self.state.current_run_up = total_equity / self.state.low_equity - 1

        if self.portfolio.performance_series.size() >= 2:
            self.state.drawdown = total_equity - self.state.high_equity

            if self.state.high_equity != 0:
                self.state.drawdown_pct = abs(self.state.drawdown / self.state.high_equity)
            self.series.add(data={self.DrawDown: self.state.drawdown,
                                  self.DrawDownPct: self.state.drawdown_pct}, timestamp=timestamp)

    def get_result(self):
        return {self.DrawDown: self.state.drawdown,
                self.DrawDownPct: self.state.drawdown_pct,
                self.HighEquity: self.state.high_equity,
                self.LowEquity: self.state.low_equity,
                self.CurrentRunUp: self.state.current_run_up,
                self.CurrentDrawDown: self.state.current_drawdown}

    def get_series(self, keys=None):
        keys = keys if keys else [self.DrawDown, self.DrawDownPct]
        return self.series.get_series(keys)
