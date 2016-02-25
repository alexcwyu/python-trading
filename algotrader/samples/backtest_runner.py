import pandas as pd
from rx.concurrency import GEventScheduler
from rx.observable import Observable, Observer
from rx.subjects import Subject
import rx
from odo import odo
import blaze
import abc

from algotrader.strategy.strategy import *
from algotrader.provider.feed import *
from algotrader.trading import *
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
