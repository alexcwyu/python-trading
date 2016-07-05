from datetime import date

from algotrader.chart.plotter import StrategyPlotter
from algotrader.event.market_data import Bar, BarSize, BarType
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.feed.csv_feed import CSVDataFeed
from algotrader.strategy.sma_strategy import SMAStrategy
from algotrader.strategy.down_2pct_strategy import Down2PctStrategy
from algotrader.strategy.strategy import BacktestingConfig
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.trading.order_mgr import order_mgr
from algotrader.trading.portfolio import Portfolio
from algotrader.utils import clock


class BacktestRunner(object):
    def __init__(self, stg):
        self.__stg = stg

    def start(self):
        clock.default_clock = clock.simluation_clock
        clock.simluation_clock.start()
        inst_data_mgr.start()
        order_mgr.start()

        self.__stg.start()


def main():
    portfolio = Portfolio(cash=100000)

    feed = CSVDataFeed()
    broker = Simulator()

    config = BacktestingConfig(broker_id=Simulator.ID,
                               feed_id=CSVDataFeed.ID,
                               data_type=Bar,
                               bar_type=BarType.Time,
                               bar_size=BarSize.D1,
                               from_date=date(2010, 1, 1), to_date=date.today())

    strategy = Down2PctStrategy("down2%", portfolio,
                                instrument=4, qty=1000,  trading_config=config )

    #strategy = SMAStrategy("sma", portfolio, instrument=4, qty=1000, trading_config=config)

    runner = BacktestRunner(strategy)
    runner.start()
    print portfolio.get_result()

    # pyfolio
    rets = strategy.get_portfolio().get_return()
    # import pyfolio as pf
    # pf.create_returns_tear_sheet(rets)
    # pf.create_full_tear_sheet(rets)

    # build in plot
    plotter = StrategyPlotter(strategy)
    plotter.plot(instrument=4)

    #import matplotlib.pyplot as plt
    #plt.show()


if __name__ == "__main__":
    main()
