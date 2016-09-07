import abc

from algotrader.config.config import Config


class FeedConfig(Config):
    __metaclass__ = abc.ABCMeta


class CSVFeedConfig(FeedConfig):
    __slots__ = (
        'path',
    )

    def __init__(self, path='../data/tradedata'):
        super(CSVFeedConfig, self).__init__(CSVFeedConfig.__class__.__name__)
        self.path = path