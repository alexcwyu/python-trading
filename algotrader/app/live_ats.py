'''
Created on 4/16/16
@author = 'jason'
'''
from algotrader.app import Application
from algotrader.provider.broker import Broker
from algotrader.utils import logger

from algotrader.model.market_data_pb2 import Bar
from algotrader.trading.clock import Clock
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.market_data_utils import BarSize


class ATSRunner(Application):
    def init(self):
        logger.info("starting ATS")

        self.app_config = self.app_config
        self.app_context = ApplicationContext(app_config=self.app_config)
        self.app_context.start()

        self.portfolio = self.app_context.portf_mgr.get_or_new_portfolio(self.app_config.portfolio_id,
                                                                         self.app_config.portfolio_initial_cash)
        self.app_context.add_startable(self.portfolio)

        self.strategy = self.app_context.stg_mgr.get_or_new_stg(self.app_config.get_app_config("stgId"),
                                                                self.app_config.get_app_config("stgCls"))
        self.app_context.add_startable(self.strategy)

    def run(self):
        self.strategy.start(self.app_context)

        logger.info("ATS started, presss Ctrl-C to stop")


def main():
    pass
    # broker_config = IBConfig(client_id=2)
    # live_trading_config = LiveTradingConfig(id=None,
    #                                         stg_id="down2%",
    #                                         stg_cls='algotrader.strategy.down_2pct_strategy.Down2PctStrategy',
    #                                         portfolio_id='test',
    #                                         instrument_ids=[4],
    #                                         subscription_types=[
    #                                             BarSubscriptionType(bar_type=Bar.Time, bar_size=BarSize.M1)],
    #                                         feed_id=Broker.IB,
    #                                         broker_id=Broker.IB,
    #                                         ref_data_mgr_type=RefDataManager.DB, clock_type=Clock.RealTime,
    #                                         persistence_config=PersistenceConfig(),
    #                                         configs=[broker_config])
    #
    # app_context = ApplicationContext(app_config=live_trading_config)
    # ATSRunner().start(app_context)


if __name__ == "__main__":
    main()
