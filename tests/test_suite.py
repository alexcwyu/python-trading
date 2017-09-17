# add comment here
import unittest

from tests.test_bar import BarTest
from tests.test_bar_aggregator import BarAggregatorTest
from tests.test_broker import SimulatorTest
from tests.test_broker_mgr import BrokerManagerTest
from tests.test_clock import ClockTest
#from tests.test_cmp_functional_backtest import TestCompareWithFunctionalBacktest
from tests.test_data_series import DataSeriesTest
from tests.test_in_memory_db import InMemoryDBTest
from tests.test_indicator import IndicatorTest
from tests.test_instrument_data import InstrumentDataTest
# from tests.test_ma import MovingAverageTest
from tests.test_market_data_processor import MarketDataProcessorTest
from tests.test_model_factory import ModelFactoryTest
from tests.test_order import OrderTest
from tests.test_order_handler import OrderHandlerTest
from tests.test_portfolio import PortfolioTest
from tests.test_position import PositionTest
from tests.test_ref_data import RefDataTest
# from tests.test_rolling import RollingApplyTest
from tests.test_ser_deser import SerializationTest
from tests.test_persistence_strategy import StrategyPersistenceTest
from tests.test_persistence_indicator import IndicatorPersistenceTest
# from tests.test_talib_wrapper import TALibSMATest
from tests.test_feed import FeedTest
from tests.test_plot import PlotTest
from tests.test_series import SeriesTest
from tests.test_data_frame import DataFrameTest

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(BarTest))
    test_suite.addTest(unittest.makeSuite(BarAggregatorTest))
    test_suite.addTest(unittest.makeSuite(SimulatorTest))
    test_suite.addTest(unittest.makeSuite(BrokerManagerTest))
    test_suite.addTest(unittest.makeSuite(ClockTest))
    test_suite.addTest(unittest.makeSuite(DataSeriesTest))
    test_suite.addTest(unittest.makeSuite(FeedTest))
    test_suite.addTest(unittest.makeSuite(IndicatorTest))
    test_suite.addTest(unittest.makeSuite(InstrumentDataTest))
    # test_suite.addTest(unittest.makeSuite(MovingAverageTest))
    test_suite.addTest(unittest.makeSuite(MarketDataProcessorTest))
    test_suite.addTest(unittest.makeSuite(ModelFactoryTest))
    test_suite.addTest(unittest.makeSuite(OrderTest))
    test_suite.addTest(unittest.makeSuite(OrderHandlerTest))
    #test_suite.addTest(unittest.makeSuite(TestCompareWithFunctionalBacktest))
    test_suite.addTest(unittest.makeSuite(InMemoryDBTest))
    #test_suite.addTest(unittest.makeSuite(PersistenceTest))
    test_suite.addTest(unittest.makeSuite(PlotTest))
    test_suite.addTest(unittest.makeSuite(PortfolioTest))
    test_suite.addTest(unittest.makeSuite(PositionTest))
    test_suite.addTest(unittest.makeSuite(RefDataTest))
    # test_suite.addTest(unittest.makeSuite(RollingApplyTest))
    test_suite.addTest(unittest.makeSuite(SerializationTest))
    test_suite.addTest(unittest.makeSuite(IndicatorPersistenceTest))
    test_suite.addTest(unittest.makeSuite(StrategyPersistenceTest))
    # test_suite.addTest(unittest.makeSuite(TALibSMATest))
    test_suite.addTest(unittest.makeSuite(SeriesTest))
    test_suite.addTest(unittest.makeSuite(DataFrameTest))
    return test_suite


mySuit = suite()

runner = unittest.TextTestRunner()
runner.run(mySuit)
# creating a new test suite
newSuite = unittest.TestSuite()
