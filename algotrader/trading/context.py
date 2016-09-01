from algotrader.provider.persistence.data_store_mgr import DataStoreManager
from algotrader.provider.provider import BrokerManager
from algotrader.provider.provider import FeedManager
from algotrader.strategy.strategy_mgr import StrategyManager
from algotrader.trading.instrument_data import InstrumentDataManager
from algotrader.trading.order_mgr import OrderManager
from algotrader.trading.portfolio_mgr import PortfolioManager
from algotrader.trading.ref_data import InMemoryRefDataManager, RefDataManager
from algotrader.trading.seq import SequenceManager
from algotrader.utils.clock import Clock, RealTimeClock, SimulationClock


class ApplicationContext(object):
    def __init__(self, application_config):
        self.application_config = application_config

        self.datastore_mgr = DataStoreManager()


        self.order_mgr = OrderManager()
        self.feed_mgr = FeedManager()
        self.broker_mgr = BrokerManager()
        self.inst_data_mgr = InstrumentDataManager()
        self.seq_mgr = SequenceManager()
        self.stg_mgr = StrategyManager()
        self.portf_mgr = PortfolioManager()
        self.ref_data_mgr = self.get_ref_data_mgr(application_config.ref_data_mgr_type)
        self.clock = self.get_clock(application_config.clock_type)

    def get_clock(clock_type=Clock.RealTime):
        if clock_type == Clock.Simulation:
            return SimulationClock()
        return RealTimeClock()

    def get_ref_data_mgr(mgr_type=RefDataManager.InMemory):
        # if mgr_type == RefDataManager.InMemory:
        return InMemoryRefDataManager()
