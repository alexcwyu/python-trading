
from algotrader.model.trading.time_series import PandasTimeSeries


class PerformanceAnalyzer(object):
    Performance = "Performance"
    StockValue = "stock_value"
    Cash = "cash"
    TotalEquity = "total_equity"

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.state = self.portfolio.state.performance
        self.series = PandasTimeSeries(self.state.series)

    def update(self, timestamp: int, current_value: float):
        self.state.stock_value = self.portfolio.stock_value
        self.state.cash = self.portfolio.cash
        self.state.total_equity = self.portfolio.total_equity
        self.series.add(
            data={self.StockValue: self.state.stock_value,
                  self.Cash: self.state.cash,
                  self.TotalEquity: self.state.total_equity},
            timestamp=timestamp)

    def get_result(self):
        return {self.StockValue: self.state.stock_value,
                self.Cash: self.state.cash,
                self.TotalEquity: self.state.total_equity}

    def get_series(self, keys=None):
        keys = keys if keys else [self.StockValue, self.Cash, self.TotalEquity]
        return self.series.get_series(keys)


    def now(self, key):
        return self.series.now(key)