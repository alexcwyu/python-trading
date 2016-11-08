from algotrader import Startable, HasId
from algotrader.config.app import ApplicationConfig
from algotrader.event.event_bus import EventBus
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
    def __init__(self, app_config=None):
        super(ApplicationContext, self).__init__()

        self.startables = []

        self.app_config = app_config if app_config else ApplicationConfig()

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

    def add_startable(self, startable):
        self.startables.append(startable)
        return startable

    def __get_clock(self):
        if self.app_config.clock_type == Clock.RealTime:
            return RealTimeClock()
        return SimulationClock()

    def __get_ref_data_mgr(self):
        if self.app_config.ref_data_mgr_type == RefDataManager.DB:
            return DBRefDataManager()
        return InMemoryRefDataManager()

    def _start(self, app_context, **kwargs):
        for startable in self.startables:
            startable.start(self)

    def _stop(self):
        for startable in reversed(self.startables):
            startable.stop()

    def get_trade_data_store(self):
        return self.provider_mgr.get(self.app_config.persistence_config.trade_ds_id)

    def get_ref_data_store(self):
        return self.provider_mgr.get(self.app_config.persistence_config.ref_ds_id)

    def get_timeseries_data_store(self):
        return self.provider_mgr.get(self.app_config.persistence_config.ts_ds_id)

    def get_seq_data_store(self):
        return self.provider_mgr.get(self.app_config.persistence_config.seq_ds_id)

