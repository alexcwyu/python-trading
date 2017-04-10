from algotrader.event.market_data import BarSize, BarType
from datetime import date
from unittest import TestCase

from algotrader.app.backtest_runner import BacktestRunner
from algotrader.config.app import BacktestingConfig
from algotrader.config.feed import CSVFeedConfig
from algotrader.config.persistence import PersistenceConfig, PersistenceMode
from algotrader.provider.broker import Broker
from algotrader.provider.feed import Feed
from algotrader.provider.persistence.data_store import DataStore
from algotrader.provider.subscription import BarSubscriptionType
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager


class StrategyPersistenceTest(TestCase):
    def test(self):
        backtest_config0 = BacktestingConfig(id="down2%-test-config", stg_id="down2%",
                                             stg_cls='algotrader.strategy.down_2pct_strategy.Down2PctStrategy',
                                             portfolio_id='test', portfolio_initial_cash=100000,
                                             instrument_ids=[4],
                                             subscription_types=[
                                                 BarSubscriptionType(bar_type=BarType.Time, bar_size=BarSize.D1)],
                                             from_date=date(1993, 1, 1), to_date=date(2017, 1, 1),
                                             broker_id=Broker.Simulator,
                                             feed_id=Feed.CSV,
                                             stg_configs={'qty': 1000},
                                             ref_data_mgr_type=RefDataManager.InMemory,
                                             persistence_config=PersistenceConfig(),
                                             provider_configs=CSVFeedConfig(path='data/tradedata')
                                             )
        app_context0 = ApplicationContext(app_config=backtest_config0)
        runner = BacktestRunner(isplot=False)

        runner.start(app_context0)

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
                                                               trade_persist_mode=PersistenceMode.Batch),
                                             provider_configs=CSVFeedConfig(path='data/tradedata'))
        app_context1 = ApplicationContext(app_config=backtest_config1)
        runner1 = BacktestRunner(isplot=False)
        runner1.start(app_context1)

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
                                             stg_configs={'qty': 1000},
                                             ref_data_mgr_type=RefDataManager.InMemory,
                                             persistence_config=PersistenceConfig(seq_ds_id=DataStore.InMemoryDB,
                                                                                  seq_persist_mode=PersistenceMode.Batch,
                                                                                  ts_ds_id=DataStore.InMemoryDB,
                                                                                  ts_persist_mode=PersistenceMode.Batch,
                                                                                  trade_ds_id=DataStore.InMemoryDB,
                                                                                  trade_persist_mode=PersistenceMode.Batch),
                                             provider_configs=CSVFeedConfig(path='data/tradedata'))
        app_context2 = ApplicationContext(app_config=backtest_config2)
        app_context2.start()
        db = app_context2.get_seq_data_store()

        runner2 = BacktestRunner(isplot=False)
        runner2.start(app_context2)

        part2_begin_result = runner2.initial_result
        part2_end_result = runner2.portfolio.get_result()

        self.assertEqual(total_begin_result, part1_begin_result)
        self.assertEqual(part1_end_result, part2_begin_result)
        self.assertEqual(total_end_result, part2_end_result)

        print
        "total begin = %s" % total_begin_result
        print
        "total end = %s" % total_end_result
        print
        "part1 begin = %s" % part1_begin_result
        print
        "part1 end = %s" % part1_end_result
        print
        "part2 begin = %s" % part2_begin_result
        print
        "part2 end = %s" % part2_end_result

        db.remove_database()
