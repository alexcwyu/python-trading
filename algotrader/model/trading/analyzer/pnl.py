from algotrader.model.trading.portfolio import Portfolio
from algotrader.model.trade_data_pb2 import *


class PnlAnalyzer(object):
    def __int__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self.performance = self.portfolio.state.performance.performance_series

    def update(self, time: int, current_value: float):
        if (len(self.performance.items)
