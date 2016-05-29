'''
Created on 4/16/16
@author = 'jason'
'''

from algotrader.provider.broker.ib.ib_broker import IBBroker
from algotrader.strategy.sma_strategy import SMAStrategy
from algotrader.strategy.strategy import LiveTradingConfig
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.trading.order_mgr import order_mgr
from algotrader.trading.portfolio import Portfolio


class ATSRunner(object):
    def __init__(self, stg):
        self.__stg = stg

    def start(self):
        # clock.default_clock = clock.realtime_clock
        inst_data_mgr.start()
        order_mgr.start()

        self.__stg.start()


def main():
    portfolio = Portfolio(cash=100000)
    broker = IBBroker()

    config = LiveTradingConfig(broker_id=IBBroker.ID,
                               feed_id=IBBroker.ID,
                               data_type=Bar,
                               bar_type=BarType.Time,
                               bar_size=BarSize.M1)

    strategy = SMAStrategy("sma", portfolio, instrument='spy', qty=1000, trading_config=config)
    # strategy = Down2PctStrategy("down2%", portfolio, instrument='spy', qty=1000, trading_config=config)

    runner = ATSRunner(strategy)
    runner.start()

    # TODO wait until stop


if __name__ == "__main__":
    main()
