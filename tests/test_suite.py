# add comment here
import unittest
from unittest import TestCase
from test_broker import SimulatorTest
from test_broker_mgr import BrokerManagerTest
from test_clock import ClockTest
from test_indicator import IndicatorTest
from test_portfolio import TestPortfolio
from test_instrument_data import InstrumentDataTest
from test_position import PositionTest
from test_ma import MovingAverageTest
# from test_ser_deser import SerializerTest
from test_market_data_processor import MarketDataProcessorTest
# from test_time_series import TimeSeriesTest
from test_order_handler import OrderHandlerTest
from test_data_series import DataSeriesTest
from test_order import OrderTest

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(SimulatorTest))
    test_suite.addTest(unittest.makeSuite(BrokerManagerTest))
    test_suite.addTest(unittest.makeSuite(ClockTest))
    test_suite.addTest(unittest.makeSuite(IndicatorTest))
    test_suite.addTest(unittest.makeSuite(TestPortfolio))
    test_suite.addTest(unittest.makeSuite(InstrumentDataTest))
    test_suite.addTest(unittest.makeSuite(PositionTest))
    test_suite.addTest(unittest.makeSuite(MovingAverageTest))
    # test_suite.addTest(unittest.makeSuite(SerializerTest))
    test_suite.addTest(unittest.makeSuite(MarketDataProcessorTest))
    # test_suite.addTest(unittest.makeSuite(TimeSeriesTest))
    test_suite.addTest(unittest.makeSuite(OrderHandlerTest))
    test_suite.addTest(unittest.makeSuite(DataSeriesTest))
    test_suite.addTest(unittest.makeSuite(OrderTest))
    return test_suite

mySuit = suite()


runner = unittest.TextTestRunner()
runner.run(mySuit)
# creating a new test suite
newSuite = unittest.TestSuite()

