from algotrader.provider.broker import Simulator
from algotrader.provider.feed import PandasCSVDataFeed
from algotrader.strategy.strategy import Strategy
from algotrader.strategy.down_2pct_strategy import Down2PctStrategy
from algotrader.trading.portfolio import Portfolio
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.trading.order_mgr import order_mgr
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
    feed = PandasCSVDataFeed(names=['spy'])
    portfolio = Portfolio(1000000)
    strategy = Down2PctStrategy("down2%", Simulator.ID, feed, portfolio, 1000)

    runner = BacktestRunner(strategy)
    runner.start()
    print portfolio.cash

    import matplotlib.pyplot as plt
    portfolio.total_equity.get_time_value_as_series().plot()

    plt.show()


if __name__ == "__main__":
    main()
