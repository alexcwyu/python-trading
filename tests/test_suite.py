# add comment here
import unittest

from test_bar import BarTest
from test_bar_aggregator import BarAggregatorTest
from test_broker import SimulatorTest
from test_broker_mgr import BrokerManagerTest
from test_clock import ClockTest
from test_cmp_functional_backtest import TestCompareWithFunctionalBacktest
from test_data_series import DataSeriesTest
from test_indicator import IndicatorTest
from test_rolling import RollingApplyTest
from test_instrument_data import InstrumentDataTest
from test_ma import MovingAverageTest
from test_market_data_processor import MarketDataProcessorTest
from test_order import OrderTest
from test_order_handler import OrderHandlerTest
from test_portfolio import PortfolioTest
from test_position import PositionTest
from test_ser_deser import SerializerTest
from test_talib_wrapper import TALibSMATest
from test_cmp_functional_backtest import TestCompareWithFunctionalBacktest
from test_bar_aggregator import BarAggregatorTest
from test_pipeline import PipelineTest
from test_pipeline_pairwise import PairwiseTest
from test_in_memory_db import InMemoryDBTest
from test_persistence import PersistenceTest
from test_strategy_persistence import StrategyPersistenceTest
#from test_data_store import DataStoreTest


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(BarTest))
    test_suite.addTest(unittest.makeSuite(BarAggregatorTest))
    # test_suite.addTest(unittest.makeSuite(SimulatorTest))
    test_suite.addTest(unittest.makeSuite(BrokerManagerTest))
    test_suite.addTest(unittest.makeSuite(ClockTest))
    test_suite.addTest(unittest.makeSuite(DataSeriesTest))
    test_suite.addTest(unittest.makeSuite(IndicatorTest))
    test_suite.addTest(unittest.makeSuite(InstrumentDataTest))
    test_suite.addTest(unittest.makeSuite(MovingAverageTest))
    test_suite.addTest(unittest.makeSuite(MarketDataProcessorTest))
    test_suite.addTest(unittest.makeSuite(OrderTest))
    test_suite.addTest(unittest.makeSuite(OrderHandlerTest))
    test_suite.addTest(unittest.makeSuite(PortfolioTest))
    test_suite.addTest(unittest.makeSuite(PositionTest))
    test_suite.addTest(unittest.makeSuite(SerializerTest))
    test_suite.addTest(unittest.makeSuite(TALibSMATest))
    test_suite.addTest(unittest.makeSuite(TestCompareWithFunctionalBacktest))
    test_suite.addTest(unittest.makeSuite(InMemoryDBTest))
    # test_suite.addTest(unittest.makeSuite(PersistenceTest))
    test_suite.addTest(unittest.makeSuite(StrategyPersistenceTest))
    # test_suite.addTest(unittest.makeSuite(DataStoreTest))
    test_suite.addTest(unittest.makeSuite(PipelineTest))
    test_suite.addTest(unittest.makeSuite(PairwiseTest))
    test_suite.addTest(unittest.makeSuite(RollingApplyTest))
    return test_suite


mySuit = suite()

runner = unittest.TextTestRunner()
runner.run(mySuit)
# creating a new test suite
newSuite = unittest.TestSuite()
