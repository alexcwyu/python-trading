'''
Created on 4/16/16
@author = 'jason'
'''

from algotrader.config.app import ApplicationConfig
from algotrader.config.broker import IBConfig
from algotrader.config.trading import LiveTradingConfig
from algotrader.event.market_data import BarSize, BarType
from algotrader.provider.broker import Broker
from algotrader.provider.persistence import DataStore
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils import logger
from algotrader.utils.clock import Clock


class ATSRunner(object):
    def __init__(self, app_config):
        self.app_config = app_config

    def start(self):
        logger.info("starting ATS")

        self.trading_config = self.app_config.get_trading_configs()[0]
        self.app_context = ApplicationContext(app_config=self.app_config)
        self.app_context.start()

        self.portfolio = self.app_context.portf_mgr.get_or_new_portfolio(self.trading_config.portfolio_id,
                                                                         self.trading_config.portfolio_initial_cash)
        self.app_context.add_startable(self.portfolio)

        self.strategy = self.app_context.stg_mgr.get_or_new_stg(self.trading_config)
        self.app_context.add_startable(self.strategy)

        self.strategy.start(self.app_context)


logger.info("ATS started, presss Ctrl-C to stop")


def stop(self):
    self.app_context.stop()


def main():
    broker_config = IBConfig(client_id=2)
    live_trading_config = LiveTradingConfig(stg_id="down2%",
                                            stg_cls='algotrader.strategy.down_2pct_strategy.Down2PctStrategy',
                                            portfolio_id='test', portfolio_initial_cash=100000,
                                            instrument_ids=[4],
                                            subscription_types=[
                                                BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.M1)],
                                            broker_id=Broker.IB,
                                            feed_id=Broker.IB)

    app_config = ApplicationConfig(None, DataStore.Mongo, DataStore.Mongo, DataStore.Mongo, DataStore.Mongo,
                                   RefDataManager.DB, Clock.RealTime,
                                   broker_config, live_trading_config)

    runner = ATSRunner(app_config)

    try:
        runner.start()

        # wait until stop
        # threading.Thread.join()
    finally:
        runner.stop()


if __name__ == "__main__":
    main()
