from unittest import TestCase

from algotrader.app.backtest_runner import BacktestRunner
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from tests import test_override


class StrategyPersistenceTest(TestCase):
    start_date = 19930101
    intrim_date = 20080101
    end_date = 20170101

    stg_override = {
        "Strategy": {
            "down2%": {
                "qty": 1000
            }
        }
    }

    def create_app_context(self, override):
        return ApplicationContext(config=Config(
            load_from_yaml("../config/backtest.yaml"),
            load_from_yaml("../config/down2%.yaml"),
            test_override,
            StrategyPersistenceTest.stg_override,
            override))

    def execute(self, conf):
        context = self.create_app_context(conf)
        runner = BacktestRunner()

        runner.start(context)

        begin_result = runner.initial_result['total_equity']
        end_result = runner.portfolio.get_result()['total_equity']
        return begin_result, end_result

    def test_result(self):
        total_begin_result, total_end_result = self.execute(
            conf={
                "Application": {
                    "portfolioId": "test",
                    "fromDate": StrategyPersistenceTest.start_date,
                    "toDate": StrategyPersistenceTest.end_date,
                    "deleteDBAtStop": True,
                    "persistenceMode": "Disable"
                }
            })

        part1_begin_result, part1_end_result = self.execute(
            conf={
                "Application": {
                    "portfolioId": "test1",
                    "fromDate": StrategyPersistenceTest.start_date,
                    "toDate": StrategyPersistenceTest.intrim_date,
                    "createDBAtStart": True,
                    "deleteDBAtStop": False,
                    "persistenceMode": "Batch"
                }
            })

        part2_begin_result, part2_end_result = self.execute(
            conf={
                "Application": {
                    "portfolioId": "test1",
                    "fromDate": StrategyPersistenceTest.intrim_date,
                    "toDate": StrategyPersistenceTest.end_date,
                    "deleteDBAtStop": True,
                    "persistenceMode": "Disable"
                }
            })

        print("total begin = %s" % total_begin_result)
        print("total end = %s" % total_end_result)
        print("part1 begin = %s" % part1_begin_result)
        print("part1 end = %s" % part1_end_result)
        print("part2 begin = %s" % part2_begin_result)
        print("part2 end = %s" % part2_end_result)

        self.assertEqual(total_begin_result, part1_begin_result)
        self.assertEqual(part1_end_result, part2_begin_result)
        self.assertEqual(total_end_result, part2_end_result)
