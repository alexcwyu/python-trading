from algotrader.performance import PortfolioAnalyzer
from algotrader.utils.time_series import DataSeries

class DrawDownType:
    DrawDown = "DrawDown"
    DrawDownPct = "DrawDown%"
    HighEquity = "HighEquity"
    LowEquity = "LowEquity"
    CurrentRunUp = "CurrentRunUp"
    CurrentDrawDown = "CurrentDrawDown"



class DrawDown(PortfolioAnalyzer):

    __slots__ = (
        'drawdown_series',
        'drawdown',
        'drawdown_pct',
        'high_equity',
        'low_equity',
        'current_run_up',
        'current_drawdown',
    )

    def __init__(self):
        self.drawdown_series = DataSeries(name='DrawDown', missing_value=0)
        self.drawdown = 0
        self.drawdown_pct = 0
        self.high_equity = 0
        self.low_equity = 0
        self.current_run_up = 0
        self.current_drawdown = 0

    def update(self, time):
        total_equity = self._portfolio.total_equity
        if self._portfolio.performance_series.size() == 1:
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

        if self._portfolio.performance_series.size() >= 2:
            self.drawdown = total_equity - self.high_equity

            if self.high_equity != 0:
                self.drawdown_pct = abs(self.drawdown / self.high_equity)
            self.drawdown_series.add({'timestamp': time,
                                      DrawDownType.DrawDown: self.drawdown,
                                      DrawDownType.DrawDownPct: self.drawdown_pct})

    def get_result(self):
        return {DrawDownType.DrawDown: self.drawdown,
                DrawDownType.DrawDownPct: self.drawdown_pct,
                DrawDownType.HighEquity: self.high_equity,
                DrawDownType.LowEquity: self.low_equity,
                DrawDownType.CurrentRunUp: self.current_run_up,
                DrawDownType.CurrentDrawDown: self.current_drawdown}

    def get_series(self):
        return self.drawdown_series.get_series([self.DrawDown, self.DrawDownPct])
