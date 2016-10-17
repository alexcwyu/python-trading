'''
Created on 4/16/16
@author = 'jason'
'''

from algotrader.app import Application
from algotrader.config.app import ApplicationConfig
from algotrader.config.broker import IBConfig
from algotrader.config.persistence import PersistenceConfig
from algotrader.config.trading import LiveTradingConfig
from algotrader.event.market_data import BarSize, BarType
from algotrader.provider.broker import Broker
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils import logger
from algotrader.utils.clock import Clock


class ATSRunner(Application):
    def init(self):
        logger.info("starting ATS")

        self.trading_config = self.app_config.get_trading_configs()[0]
        self.app_context = ApplicationContext(app_config=self.app_config)
        self.app_context.start()

        self.portfolio = self.app_context.portf_mgr.get_or_new_portfolio(self.trading_config.portfolio_id,
                                                                         self.trading_config.portfolio_initial_cash)
        self.app_context.add_startable(self.portfolio)

        self.strategy = self.app_context.stg_mgr.get_or_new_stg(self.trading_config)
        self.app_context.add_startable(self.strategy)

    def run(self):
        self.strategy.start(self.app_context)

        logger.info("ATS started, presss Ctrl-C to stop")



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

    app_config = ApplicationConfig(None, RefDataManager.DB, Clock.RealTime, PersistenceConfig(),
                                   broker_config, live_trading_config)
    app_context = ApplicationContext(app_config=app_config)
    ATSRunner().start(app_context)


if __name__ == "__main__":
    main()
