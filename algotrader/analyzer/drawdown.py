from algotrader.analyzer import Analyzer
from algotrader.trading.data_series import DataSeries


class DrawDownAnalyzer(Analyzer):
    DrawDown = "DrawDown"
    DrawDownPct = "DrawDown%"
    HighEquity = "HighEquity"
    LowEquity = "LowEquity"
    CurrentRunUp = "CurrentRunUp"
    CurrentDrawDown = "CurrentDrawDown"

    def __init__(self, portfolio, state):
        self.portfolio = portfolio
        self.state = state
        self.series = DataSeries(self.state.drawdown.series)

    def update(self, timestamp: int, total_equity: float):
        if self.portfolio.performance.series.size() == 1:
            self.state.drawdown.low_equity = total_equity
            self.state.drawdown.high_equity = total_equity
        else:
            if total_equity > self.state.drawdown.high_equity:
                self.state.drawdown.high_equity = total_equity
                self.state.drawdown.low_equity = total_equity
                self.state.drawdown.current_drawdown = 0
            elif total_equity < self.state.drawdown.low_equity:
                self.state.drawdown.low_equity = total_equity
                self.state.drawdown.current_run_up = 0
            elif total_equity > self.state.drawdown.low_equity and total_equity < self.state.drawdown.high_equity:
                self.state.drawdown.current_drawdown = 1 - total_equity / self.state.drawdown.high_equity
                self.state.drawdown.current_run_up = total_equity / self.state.drawdown.low_equity - 1

        if self.portfolio.performance.series.size() >= 2:
            self.state.drawdown.last_drawdown = total_equity - self.state.drawdown.high_equity

            if self.state.drawdown.high_equity != 0:
                self.state.drawdown.last_drawdown_pct = abs(
                    self.state.drawdown.last_drawdown / self.state.drawdown.high_equity)
            self.series.add(data={self.DrawDown: self.state.drawdown.last_drawdown,
                                  self.DrawDownPct: self.state.drawdown.last_drawdown_pct}, timestamp=timestamp)

    def get_result(self):
        return {self.DrawDown: self.state.drawdown.last_drawdown,
                self.DrawDownPct: self.state.drawdown.last_drawdown_pct,
                self.HighEquity: self.state.drawdown.high_equity,
                self.LowEquity: self.state.drawdown.low_equity,
                self.CurrentRunUp: self.state.drawdown.current_run_up,
                self.CurrentDrawDown: self.state.drawdown.current_drawdown}

    def get_series(self, keys=None):
        keys = keys if keys else [self.DrawDown, self.DrawDownPct]
        return self.series.get_series(keys)

    def last_drawdown(self) -> float:
        return self.state.drawdown.last_drawdown

    def last_drawdown_pct(self) -> float:
        return self.state.drawdown.last_drawdown_pct

    def high_equity(self) -> float:
        return self.state.drawdown.high_equity

    def low_equity(self) -> float:
        return self.state.drawdown.low_equity

    def current_run_up(self) -> float:
        return self.state.drawdown.current_run_up

    def current_drawdown(self) -> float:
        return self.state.drawdown.current_drawdown
