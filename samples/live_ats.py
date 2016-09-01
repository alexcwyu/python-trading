'''
Created on 4/16/16
@author = 'jason'
'''

from algotrader.config.trading import LiveTradingConfig
from algotrader.event.market_data import BarSize, BarType
from algotrader.provider.broker.ib.ib_broker import IBBroker
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.strategy.down_2pct_strategy import Down2PctStrategy
from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.trading.order_mgr import order_mgr
from algotrader.trading.portfolio import Portfolio
from algotrader.utils import logger


class ATSRunner(object):
    def __init__(self, stg):
        self.__stg = stg

    def start(self):
        inst_data_mgr.start()
        order_mgr.start()
        self.__stg.start()


def main():
    portfolio = Portfolio(portf_id='test', cash=100000)
    broker = IBBroker(client_id=2)

    config = LiveTradingConfig(portfolio_id='test',
                               instrument_ids=[4],
                               subscription_types=[BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.M1)],
                               broker_id=IBBroker.ID,
                               feed_id=IBBroker.ID)

    # strategy = SMAStrategy("sma", qty=1000, trading_config=config)
    strategy = Down2PctStrategy("down2%", qty=1000, trading_config=config)

    runner = ATSRunner(strategy)

    logger.info("starting ATS")

    runner.start()

    logger.info("ATS started, presss Ctrl-C to stop")

    # wait until stop
    # threading.Thread.join()


if __name__ == "__main__":
    main()
