from algotrader.performance import PortfolioAnalyzer
from algotrader.utils.time_series import DataSeries


class Pnl(PortfolioAnalyzer):
    Pnl = "Pnl"

    __slots__ = (
        'pnl_series',
        'pnl'
    )

    def __init__(self):
        self.pnl_series = DataSeries(name=Pnl.Pnl, missing_value=0)
        self.pnl = 0

    def update(self, time):
        if self.portfolio.performance_series.size() >= 2:
            self.pnl = self.portfolio.performance_series.get_by_idx(-1,
                                                                    'total_equity') - self.portfolio.performance_series.get_by_idx(
                -2, 'total_equity')
            self.pnl_series.add({'timestamp': time, Pnl.Pnl: self.pnl})

    def get_result(self):
        return {Pnl.Pnl: self.pnl}

    def get_series(self):
        return {Pnl.Pnl: self.pnl_series.get_series(Pnl.Pnl)}

    def id(self):
        return '%s.%s' % (self.portfolio.id(), Pnl.Pnl)
