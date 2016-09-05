from algotrader.provider import ProviderManager
from algotrader.provider.feed import Feed
from algotrader.provider.feed.csv_feed import CSVDataFeed
from algotrader.provider.feed.pandas_memory import PandasMemoryDataFeed
from algotrader.provider.feed.pandas_web import GoogleDataFeed, YahooDataFeed

class FeedManager(ProviderManager):
    def __init__(self, app_context):
        super(FeedManager, self).__init__()
        self.app_context = app_context

        self.add(CSVDataFeed())
        self.add(PandasMemoryDataFeed())
        self.add(GoogleDataFeed())
        self.add(YahooDataFeed())

    def add(self, provider):
        if provider and isinstance(provider, Feed):
            super(FeedManager, self).add(provider)

    def _start(self):
        self.app_config.feed_configs
        ## TODO foreach config: init feed with config


feed_mgr = FeedManager()