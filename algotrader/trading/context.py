from typing import Dict

from algotrader import Startable
from algotrader.config import Config
from algotrader.event.event_bus import EventBus
from algotrader.model.model_factory import ModelFactory
from algotrader.provider.persistence.data_store import DataStore
from algotrader.provider.provider_mgr import ProviderManager
from algotrader.strategy.strategy_mgr import StrategyManager
from algotrader.trading.account_mgr import AccountManager
from algotrader.trading.instrument_data import InstrumentDataManager
from algotrader.trading.order_mgr import OrderManager
from algotrader.trading.portfolio_mgr import PortfolioManager
from algotrader.trading.ref_data import InMemoryRefDataManager, RefDataManager, DBRefDataManager
from algotrader.trading.seq_mgr import SequenceManager
from algotrader.utils.clock import Clock, RealTimeClock, SimulationClock


class ApplicationContext(Startable):
    def __init__(self, config: Dict = None):
        super(ApplicationContext, self).__init__()

        self.startables = []

        self.app_config = Config(config)

        self.clock = self.add_startable(self.__get_clock())
        self.provider_mgr = self.add_startable(ProviderManager())

        self.seq_mgr = self.add_startable(SequenceManager())

        self.inst_data_mgr = self.add_startable(InstrumentDataManager())
        self.ref_data_mgr = self.add_startable(self.__get_ref_data_mgr())

        self.order_mgr = self.add_startable(OrderManager())
        self.acct_mgr = self.add_startable(AccountManager())
        self.portf_mgr = self.add_startable(PortfolioManager())
        self.stg_mgr = self.add_startable(StrategyManager())

        self.event_bus = EventBus()
        self.model_factory = ModelFactory

    def add_startable(self, startable: Startable) -> Startable:
        self.startables.append(startable)
        return startable

    def __get_clock(self) -> Clock:
        if self.app_config.get("Application", "clockId") == Clock.RealTime:
            return RealTimeClock()
        return SimulationClock()

    def __get_ref_data_mgr(self) -> RefDataManager:
        if self.app_config.get("Application", "dataStoreId") == DataStore.InMemoryDB:
            return InMemoryRefDataManager()
        return DBRefDataManager()

    def _start(self, app_context, **kwargs):
        for startable in self.startables:
            startable.start(self)

    def _stop(self):
        for startable in reversed(self.startables):
            startable.stop()

    def get_data_store(self) -> DataStore:
        return self.provider_mgr.get(self.app_config.get("Application", "dataStoreId"))

    def get_broker(self):
        pass

    def get_feed(self):
        pass

    def get_portfolio(self):
        pass

