import datetime
from unittest import TestCase

from algotrader.event.market_data import Bar, Trade, Quote
from algotrader.utils.ser_deser import MsgPackSerializer


class SerializerTest(TestCase):
    def setUp(self):
        self.serializer = MsgPackSerializer()

    def test_bar(self):
        item = Bar(open=18, high=19, low=17, close=17.5, vol=100, instrument='HSI', timestamp=datetime.datetime.now())
        self.ser_deser(item)

    def test_quote(self):
        item = Quote(bid=18, ask=19, bid_size=200, ask_size=500, instrument='HSI', timestamp=datetime.datetime.now())
        self.ser_deser(item)

    def test_trade(self):
        item = Trade(price=20, size=200, instrument='HSI', timestamp=datetime.datetime.now())
        self.ser_deser(item)

    def ser_deser(self, item):
        packed = self.serializer.serialize(item)
        unpacked = self.serializer.deserialize(packed)

        assert item == unpacked
