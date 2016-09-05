from algotrader import Startable
from algotrader.provider.persistence.data_store_mgr import DataStoreManager
from algotrader.provider.broker.broker_mgr import BrokerManager
from algotrader.provider.feed.feed_mgr import FeedManager
from algotrader.strategy.strategy_mgr import StrategyManager
from algotrader.trading.account_mgr import AccountManager
from algotrader.trading.instrument_data import InstrumentDataManager
from algotrader.trading.order_mgr import OrderManager
from algotrader.trading.portfolio_mgr import PortfolioManager
from algotrader.trading.ref_data import InMemoryRefDataManager, RefDataManager, DBRefDataManager
from algotrader.trading.seq import SequenceManager
from algotrader.utils.clock import Clock, RealTimeClock, SimulationClock


class ApplicationContext(Startable):
    def __init__(self, app_config):
        super(ApplicationContext, self).__init__()

        self.startables = []

        self.app_config = app_config

        self.clock = self.add_startable(self.get_clock())
        self.datastore_mgr = self.add_startable(DataStoreManager(self))
        self.feed_mgr = self.add_startable(FeedManager(self))
        self.broker_mgr = self.add_startable(BrokerManager(self))
        self.seq_mgr = self.add_startable(SequenceManager(self))

        self.inst_data_mgr = self.add_startable(InstrumentDataManager(self))
        self.ref_data_mgr = self.add_startable(self.get_ref_data_mgr())

        self.order_mgr = self.add_startable(OrderManager(self))
        self.acct_mgr = self.add_startable(AccountManager(self))
        self.portf_mgr = self.add_startable(PortfolioManager(self))
        self.stg_mgr = self.add_startable(StrategyManager(self))

    def add_startable(self, startable):
        self.startables.append(startable)
        return startable

    def get_clock(self):
        if self.app_config.clock_type == Clock.Simulation:
            return SimulationClock(self)
        return RealTimeClock(self)

    def get_ref_data_mgr(self):
        if self.app_config.ref_data_mgr_type == RefDataManager.InMemory:
            return InMemoryRefDataManager(self)
        return DBRefDataManager(self)

    def _start(self):
        for startable in self.startables:
            startable.start()

    def _stop(self):
        for startable in self.startables:
            startable.stop()

    def get_trade_data_store(self):
        return self.datastore_mgr.get(self.app_config.trade_datastore_id)

    def get_ref_data_store(self):
        return self.datastore_mgr.get(self.app_config.ref_datastore_id)

    def get_timeseries_data_store(self):
        return self.datastore_mgr.get(self.app_config.time_series_datastore_id)

    def get_seq_data_store(self):
        return self.datastore_mgr.get(self.app_config.seq_datastore_id)
