from datetime import date

from algotrader.event.market_data import Bar, BarType, BarSize
from algotrader.provider.broker.ib.ib_broker import IBBroker
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.feed.csv_feed import CSVDataFeed
from algotrader.provider.persistence.persist import Persistable
from algotrader.utils.clock import realtime_clock, simluation_clock


class Config(Persistable):
    pass


class ApplicationConfig(Config):
    pass

class TradingConfig(Config):
    def __init__(self, broker_id, feed_id,
                 data_type,
                 bar_type,
                 bar_size, clock):
        self.broker_id = broker_id
        self.feed_id = feed_id
        self.data_type = data_type
        self.bar_type = bar_type
        self.bar_size = bar_size
        self.clock = clock


class LiveTradingConfig(TradingConfig):
    def __init__(self, broker_id=IBBroker.ID, feed_id=IBBroker.ID, data_type=Bar, bar_type=BarType.Time,
                 bar_size=BarSize.S1):
        super(LiveTradingConfig, self).__init__(broker_id=broker_id, feed_id=feed_id, data_type=data_type,
                                                bar_type=bar_type, bar_size=bar_size, clock=realtime_clock)


class BacktestingConfig(TradingConfig):
    def __init__(self, broker_id=Simulator.ID, feed_id=CSVDataFeed.ID, data_type=Bar, bar_type=BarType.Time,
                 bar_size=BarSize.D1, from_date=date(2010, 1, 1), to_date=date.today()):
        super(BacktestingConfig, self).__init__(broker_id=broker_id, feed_id=feed_id, data_type=data_type,
                                                bar_type=bar_type, bar_size=bar_size, clock=simluation_clock)
        self.from_date = from_date
        self.to_date = to_date
