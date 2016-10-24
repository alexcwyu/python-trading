from datetime import date
from unittest import TestCase

from algotrader.app.backtest_runner import BacktestRunner
from algotrader.config.app import ApplicationConfig
from algotrader.config.persistence import PersistenceConfig, PersistenceMode
from algotrader.config.app import BacktestingConfig
from algotrader.event.market_data import BarSize, BarType
from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed
from algotrader.provider.persistence import DataStore
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock
from algotrader.trading.context import ApplicationContext


class StrategyPersistenceTest(TestCase):
    def test(self):
        backtest_config = BacktestingConfig(id="down2%-test-config", stg_id="down2%",
                                            stg_cls='algotrader.strategy.down_2pct_strategy.Down2PctStrategy',
                                            portfolio_id='test', portfolio_initial_cash=100000,
                                            instrument_ids=[4],
                                            subscription_types=[
                                                BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                                            from_date=date(1993, 1, 1), to_date=date(2017, 1, 1),
                                            broker_id=Broker.Simulator,
                                            feed_id=Feed.CSV,
                                            stg_configs={'qty': 1000},
                                            ref_data_mgr_type=RefDataManager.InMemory, persistence_config=PersistenceConfig())
        app_context = ApplicationContext(app_config=backtest_config)
        runner = BacktestRunner(plot = False)

        runner.start(app_context)

        total_begin_result = runner.initial_result
        total_end_result = runner.portfolio.get_result()

        backtest_config1 = BacktestingConfig(id="down2%-test-config_1", stg_id="down2%_1",
                                             stg_cls='algotrader.strategy.down_2pct_strategy.Down2PctStrategy',
                                             portfolio_id='test_1', portfolio_initial_cash=100000,
                                             instrument_ids=[4],
                                             subscription_types=[
                                                 BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                                             from_date=date(1993, 1, 1), to_date=date(2008, 1, 1),
                                             broker_id=Broker.Simulator,
                                             feed_id=Feed.CSV,
                                             stg_configs={'qty': 1000},
                                             ref_data_mgr_type=RefDataManager.InMemory, persistence_config=
                                             PersistenceConfig(seq_ds_id=DataStore.InMemoryDB,
                                                               seq_persist_mode=PersistenceMode.Batch,
                                                               ts_ds_id=DataStore.InMemoryDB,
                                                               ts_persist_mode=PersistenceMode.Batch,
                                                               trade_ds_id=DataStore.InMemoryDB,
                                                               trade_persist_mode=PersistenceMode.Batch))
        runner1 = BacktestRunner(backtest_config1)
        runner1.start()
        runner1.stop()

        part1_begin_result = runner1.initial_result
        part1_end_result = runner1.portfolio.get_result()

        backtest_config2 = BacktestingConfig(id="down2%-test-config_1", stg_id="down2%_1",
                                             stg_cls='algotrader.strategy.down_2pct_strategy.Down2PctStrategy',
                                             portfolio_id='test_1', portfolio_initial_cash=100000,
                                             instrument_ids=[4],
                                             subscription_types=[
                                                 BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                                             from_date=date(2008, 1, 1), to_date=date(2017, 1, 1),
                                             broker_id=Broker.Simulator,
                                             feed_id=Feed.CSV,
                                             stg_configs={'qty': 1000})
        app_config2 = ApplicationConfig("down2%_1", RefDataManager.InMemory, Clock.Simulation,
                                        PersistenceConfig(seq_ds_id=DataStore.InMemoryDB,
                                                          seq_persist_mode=PersistenceMode.Batch,
                                                          ts_ds_id=DataStore.InMemoryDB,
                                                          ts_persist_mode=PersistenceMode.Batch,
                                                          trade_ds_id=DataStore.InMemoryDB,
                                                          trade_persist_mode=PersistenceMode.Batch),
                                        backtest_config2)
        runner2 = BacktestRunner(app_config2)
        runner2.start()

        db = runner2.app_context.get_seq_data_store()
        part2_begin_result = runner2.initial_result
        part2_end_result = runner2.portfolio.get_result()

        self.assertEqual(total_begin_result, part1_begin_result)
        self.assertEqual(part1_end_result, part2_begin_result)
        self.assertEqual(total_end_result, part2_end_result)

        print "total begin = %s"%total_begin_result
        print "total end = %s"%total_end_result
        print "part1 begin = %s"%part1_begin_result
        print "part1 end = %s"%part1_end_result
        print "part2 begin = %s"%part2_begin_result
        print "part2 end = %s"%part2_end_result

        runner2.stop()
        db.remove_database()

if __name__== "__main__":
    import unittest
    runner = unittest.TextTestRunner()
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(StrategyPersistenceTest))
    runner.run(test_suite)

    # creating a new test suite
    newSuite = unittest.TestSuite()