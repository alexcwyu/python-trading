from unittest import TestCase

from algotrader.trading.config import Config, load_from_yaml


class ConfigTest(TestCase):
    def test_multiple(self):
        app_config = Config(
            load_from_yaml("../config/backtest.yaml"),
            load_from_yaml("../config/down2%.yaml"))
        self.assertEquals(1, app_config.get_strategy_config("down2%", "qty"))
