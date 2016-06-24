from algotrader.performance import PortfolioAnalyzer
from algotrader.utils.time_series import DataSeries


class DrawDown(PortfolioAnalyzer):
    DrawDown = "DrawDown"
    DrawDownPct = "DrawDown%"
    HighEquity = "HighEquity"
    LowEquity = "LowEquity"
    CurrentRunUp = "CurrentRunUp"
    CurrentDrawDown = "CurrentDrawDown"

    def __init__(self):
        self.drawdown_series = DataSeries(name=DrawDown)
        self.drawdown = 0
        self.drawdown_pct = 0
        self.high_equity = 0
        self.low_equity = 0
        self.current_run_up = 0
        self.current_drawdown = 0

    def update(self, time):
        total_equity = self.portfolio.total_equity
        if self.portfolio.performance_series.size() == 1:
            self.low_equity = total_equity
            self.high_equity = total_equity
        else:
            if total_equity > self.high_equity:
                self.high_equity = total_equity
                self.low_equity = total_equity
                self.current_drawdown = 0
            elif total_equity < self.low_equity:
                self.low_equity = total_equity
                self.current_run_up = 0
            elif total_equity > self.low_equity and total_equity < self.high_equity:
                self.current_drawdown = 1 - total_equity / self.high_equity
                self.current_run_up = total_equity / self.low_equity - 1

        if self.portfolio.performance_series.size() >= 2:
            self.drawdown = total_equity - self.high_equity

            if self.high_equity != 0:
                self.drawdown_pct = abs(self.drawdown / self.high_equity)
            self.drawdown_series.add({'timestamp': time,
                                      DrawDown.DrawDown: self.drawdown,
                                      DrawDown.DrawDownPct: self.drawdown_pct})

    def get_result(self):
        return {DrawDown.DrawDown: self.drawdown,
                DrawDown.DrawDownPct: self.drawdown_pct,
                DrawDown.HighEquity: self.high_equity,
                DrawDown.LowEquity: self.low_equity,
                DrawDown.CurrentRunUp: self.current_run_up,
                DrawDown.CurrentDrawDown: self.current_drawdown}

    def get_series(self):
        return self.drawdown_series.get_series([self.DrawDown, self.DrawDownPct])
