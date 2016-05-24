'''
Created on 4/16/16
@author = 'jason'
'''

import time
from algotrader.chart.plotter import StrategyPlotter
from algotrader.provider.broker.simulator import Simulator
from algotrader.provider.feed.csv import PandasCSVDataFeed
from algotrader.strategy.down_2pct_strategy import Down2PctStrategy
from algotrader.strategy.sma_strategy import SMAStrategy
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.trading.order_mgr import order_mgr
from algotrader.trading.portfolio import Portfolio
from algotrader.utils import clock
from algotrader.provider.broker.ib.ib_broker import IbGateway
from algotrader.utils.betterthread import Thread as bThread
from algotrader.utils.clock import default_clock
from algotrader.utils import logger

class StoppableSingleStrategyATS(bThread):
    def run(self):
        inst_data_mgr.start()
        order_mgr.start()
        self.ibgateway = IbGateway()
        self.ibgateway.start()
        logger.debug("[%s] Error: %s" % (self.__class__.__name__, "ibgateway started!"))
        self.ibgateway.req_mktdata()

    def shutdown(self):
        del self.ibgateway



class ATSRunner(object):
    def __init__(self, stg):
        self.__stg = stg

    def start(self):
        inst_data_mgr.start()
        order_mgr.start()
        self.ibgateway = IbGateway()
        self.ibgateway.start()
        logger.debug("[%s] Error: %s" % (self.__class__.__name__, "ibgateway started!"))
        self.ibgateway.req_mktdata()


# def main():
    #feed = PandasCSVDataFeed(names=['spy'])
    # portfolio = Portfolio(cash=100000)
    #strategy = SMAStrategy("sma", Simulator.ID, feed, portfolio, instrument='spy', qty=1000)
    #strategy = Down2PctStrategy("down2%", Simulator.ID, feed, portfolio, instrument='spy', qty=1000)

    # runner = SingleStrategyATSRunner(None)
    # runner.start()

    # try:
    #     while True:
    #         time.sleep(100000000000)
    # except KeyboardInterrupt as e:
    #     print "Keyboard Interupt recieved!"


if __name__ == "__main__":
    # TODO: Call IB to get the account value
    portfolio = Portfolio(cash=100000)
    #t = StoppableSingleStrategyATS()
    # t.start()


    runner = ATSRunner(None)
    runner.start()


    print("Press <Ctrl-C> to stop thread")
    while True:
        try:
            time.sleep(1000000)
        except KeyboardInterrupt:
            exit("Keyboard interrupt - waiting for thread to finish...")
