from unittest import TestCase

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.utils.clock import simluation_clock


class ClockTest(TestCase):
    def test_current_date_time_with_bar(self):
        timestamp = 1466441077
        bar = Bar(timestamp=timestamp)
        simluation_clock.on_bar(bar)
        self.assertEquals(timestamp, simluation_clock.current_date_time())

    def test_current_date_time_with_quote(self):
        timestamp = 1466441077
        quote = Quote(timestamp=timestamp)
        simluation_clock.on_quote(quote)
        self.assertEquals(timestamp, simluation_clock.current_date_time())

    def test_current_date_time_with_trade(self):
        timestamp = 1466441077
        trade = Trade(timestamp=timestamp)
        simluation_clock.on_trade(trade)
        self.assertEquals(timestamp, simluation_clock.current_date_time())
