import datetime
from unittest import TestCase

from nose_parameterized import parameterized, param

from algotrader.event.market_data import Bar, Trade, Quote
from algotrader.utils.ser_deser import MsgPackSerializer, JsonSerializer

params = [
    param(MsgPackSerializer()),
    param(JsonSerializer())
]
class SerializerTest(TestCase):
    @parameterized.expand(params)
    def test_bar(self, serializer):
        item = Bar(open=18, high=19, low=17, close=17.5, vol=100, instrument='HSI', timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_quote(self, serializer):
        item = Quote(bid=18, ask=19, bid_size=200, ask_size=500, instrument='HSI', timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(serializer, item)

    @parameterized.expand(params)
    def test_trade(self, serializer):
        item = Trade(price=20, size=200, instrument='HSI', timestamp=datetime.datetime.now())
        SerializerTest.ser_deser(serializer, item)

    @staticmethod
    def ser_deser(serializer, item):
        packed = serializer.serialize(item)
        unpacked = serializer.deserialize(packed)

        assert item == unpacked
