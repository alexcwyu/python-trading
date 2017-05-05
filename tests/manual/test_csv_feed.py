from unittest import TestCase

from algotrader.trading.config import Config
from algotrader.trading.context import ApplicationContext
from algotrader.trading.event import EventLogger
from algotrader.utils.market_data import *


class CSVTest(TestCase):
    def test_loaded_bar(self):
        app_config = Config({"DataStore": {"InMemory": {"file": "../../data/algotrader_db.p"}},
                             "Feed": {"CSV": {"path": "../data/tradedata"}}})

        app_context = ApplicationContext(app_config=app_config)
        app_context.start()

        feed_id = "CSV"
        feed = app_context.provider_mgr.get(feed_id)
        feed.start(app_context)

        # logger.setLevel(logging.DEBUG)
        eventLogger = EventLogger()
        eventLogger.start(app_context)

        instruments = app_context.ref_data_mgr.get_insts_by_ids(["SPY@NYSEARCA"])
        for sub_req in build_subscription_requests(feed_id, instruments,
                                                   ["Bar.Yahoo.Time.D1"],
                                                   20100101,
                                                   20170101):
            feed.subscribe_mktdata(sub_req)

        self.assertTrue(eventLogger.count[Bar] > 0)
        self.assertTrue(eventLogger.count[Trade] == 0)
        self.assertTrue(eventLogger.count[Quote] == 0)
