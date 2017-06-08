from algotrader import Context
from algotrader.model.model_factory import ModelFactory
from algotrader.provider import ProviderManager
from algotrader.provider.broker import Broker
from algotrader.provider.datastore import DataStore
from algotrader.provider.feed import Feed
from algotrader.strategy import StrategyManager
from algotrader.trading.account import AccountManager
from algotrader.trading.clock import Clock, RealTimeClock, SimulationClock
from algotrader.trading.config import Config
from algotrader.trading.event import EventBus
from algotrader.trading.instrument_data import InstrumentDataManager
from algotrader.trading.order import OrderManager
from algotrader.trading.portfolio import Portfolio, PortfolioManager
from algotrader.trading.ref_data import RefDataManager
from algotrader.trading.sequence import SequenceManager


class ApplicationContext(Context):
    def __init__(self, config: Config = None):
        super(ApplicationContext, self).__init__()

        self.config = config if config else Config()

        self.clock = self.add_startable(self.__get_clock())
        self.provider_mgr = self.add_startable(ProviderManager())

        self.seq_mgr = self.add_startable(SequenceManager())

        self.inst_data_mgr = self.add_startable(InstrumentDataManager())
        self.ref_data_mgr = self.add_startable(RefDataManager())

        self.order_mgr = self.add_startable(OrderManager())
        self.acct_mgr = self.add_startable(AccountManager())
        self.portf_mgr = self.add_startable(PortfolioManager())
        self.stg_mgr = self.add_startable(StrategyManager())

        self.event_bus = EventBus()
        self.model_factory = ModelFactory

    def __get_clock(self) -> Clock:
        if self.config.get_app_config("clockId", Clock.Simulation) == Clock.RealTime:
            return RealTimeClock()
        return SimulationClock()

    def get_data_store(self) -> DataStore:
        return self.provider_mgr.get(self.config.get_app_config("dataStoreId"))

    def get_broker(self) -> Broker:
        return self.provider_mgr.get(self.config.get_app_config("brokerId"))

    def get_feed(self) -> Feed:
        return self.provider_mgr.get(self.config.get_app_config("feedId"))

    def get_portfolio(self) -> Portfolio:
        return self.portf_mgr.get_or_new_portfolio(self.config.get_app_config("dataStoreId"),
                                                   self.config.get_app_config("portfolioInitialcash"))
