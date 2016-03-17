from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.technical import bollinger
from pyalgotrade.stratanalyzer import sharpe

from pyalgotrade.broker import fillstrategy

class Down2Pct(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, pct = 0.02, qty = 1000):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__prev_bar = None
        self.__curr_bar = None
        self.day_count = 0
        self.entered = False
        self.pct = pct
        self.qty = qty
        self.getBroker().setFillStrategy(fillstrategy.DefaultStrategy(volumeLimit = 1))


    def onBars(self, bars):
        shares = self.getBroker().getShares(self.__instrument)

        bar = bars[self.__instrument]
        self.__prev_bar = self.__curr_bar
        self.__curr_bar = bar


        if not self.entered:
            roc = self.roc()
            if roc < -self.pct:

                self.getLogger().info("%s,B,%s" % (bar.getDateTime(), bar.getClose()))
                self.marketOrder(self.__instrument, self.qty)
                self.day_count = 0
                self.entered = True
        else:
            self.day_count += 1
            if self.day_count >= 5:
                self.getLogger().info("%s,S,%s" % (bar.getDateTime(), bar.getClose()))
                self.marketOrder(self.__instrument, -1 * self.qty)
                self.entered = False

    def roc(self):
        if self.__curr_bar and self.__prev_bar:
            return (self.__curr_bar.getClose() - self.__prev_bar.getClose()) / self.__prev_bar.getClose()
        return 0


def main(plot):
    instrument = "spy"

    # Download the bars.
    feed = yahoofinance.build_feed([instrument], 1993, 2016, ".")

    strat = Down2Pct(feed, instrument)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)

    print strat.getBroker().getEquity()
    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)

    print strat.getBroker().getEquity()
    if plot:
        plt.plot()


if __name__ == "__main__":
    main(True)