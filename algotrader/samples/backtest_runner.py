from algotrader.provider.broker import Simulator
from algotrader.provider.feed import PandasCSVDataFeed
from algotrader.strategy.strategy import Strategy
from algotrader.trading import Portfolio
from algotrader.trading
from algotrader.trading import clock


class BacktestRunner:
    def __init__(self, stg):
        self.__stg = stg

    def start(self):
        clock.default_clock = clock.simluation_clock
        clock.simluation_clock.start()
        inst_data_mgr.start()
        order_mgr.start()

        self.__stg.start()


def main():
    feed = PandasCSVDataFeed(names=['goog', 'msft'])
    portfolio = Portfolio(100000)
    strategy = Strategy("Demo", Simulator.ID, feed, portfolio)

    runner = BacktestRunner(strategy)
    runner.start()


if __name__ == "__main__":
    main()
