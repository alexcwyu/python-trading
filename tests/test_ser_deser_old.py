import datetime
from unittest import TestCase

from nose_parameterized import parameterized, param

from algotrader.technical.ma import SMA
from algotrader.trading.context import ApplicationContext
from poc.ser_deser import MsgPackSerializer, JsonSerializer, MapSerializer
from tests.sample_factory import *

params = [
    param('MsgPackSerializer', MsgPackSerializer),
    param('JsonSerializer', JsonSerializer),
    param('MapSerializer', MapSerializer)
]


class SerializerTest(TestCase):
    def setUp(self):
        self.factory = SampleFactory()

    # Market Data Event
    @parameterized.expand(params)
    def test_bar(self, name, serializer):
        item = self.factory.sample_bar()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_quote(self, name, serializer):
        item = self.factory.sample_quote()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_trade(self, name, serializer):
        item = self.factory.sample_trade()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_market_depth(self, name, serializer):
        item = self.factory.sample_market_depth()
        SerializerTest.ser_deser(name, serializer, item)

    # Order Event
    @parameterized.expand(params)
    def test_new_order_request(self, name, serializer):
        item = self.factory.sample_new_order_request()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_order_replace_request(self, name, serializer):
        item = self.factory.sample_order_replace_request()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_order_cancel_request(self, name, serializer):
        item = self.factory.sample_order_cancel_request()
        SerializerTest.ser_deser(name, serializer, item)

    # Execution Event
    @parameterized.expand(params)
    def test_order_status_update(self, name, serializer):
        item = self.factory.sample_order_status_update()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_execution_report(self, name, serializer):
        item = self.factory.sample_execution_report()
        SerializerTest.ser_deser(name, serializer, item)

    # Account Event
    @parameterized.expand(params)
    def test_account_update(self, name, serializer):
        item = self.factory.sample_account_update()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_portfolio_update(self, name, serializer):
        item = self.factory.sample_portfolio_update()
        SerializerTest.ser_deser(name, serializer, item)

    # Ref Data
    @parameterized.expand(params)
    def test_instrument(self, name, serializer):
        item = self.factory.sample_instrument()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_exchange(self, name, serializer):
        item = self.factory.sample_exchange()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_currency(self, name, serializer):
        item = self.factory.sample_currency()
        SerializerTest.ser_deser(name, serializer, item)

    # Trade Data


    @parameterized.expand(params)
    def test_order(self, name, serializer):
        item = self.factory.sample_order_state()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_account(self, id, serializer):
        item = self.factory.sample_account_state()

        SerializerTest.ser_deser(id, serializer, item)

    @parameterized.expand(params)
    def test_time_series(self, name, serializer):
        item = self.factory.sample_time_series()

        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_indicator(self, name, serializer):
        self.app_context = ApplicationContext()

        bar = self.app_context.inst_data_mgr.get_series("bar")
        sma = SMA(bar.name, 'close', 1, missing_value=0)
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(0, 3)
        t3 = t2 + datetime.timedelta(0, 3)

        bar.add({"timestamp": t1, "close": 2.0, "open": 0})
        bar.add({"timestamp": t2, "close": 2.4, "open": 1.4})

        bar.add({"timestamp": t3, "close": 2.8, "open": 1.8})

        SerializerTest.ser_deser(name, serializer, sma)

    @parameterized.expand(params)
    def test_portfolio(self, name, serializer):
        item = self.factory.sample_portfolio_state()
        SerializerTest.ser_deser(name, serializer, item)

    @parameterized.expand(params)
    def test_strategy(self, name, serializer):
        stg = self.factory.sample_strategy_state()

        SerializerTest.ser_deser(name, serializer, stg)

    @staticmethod
    def ser_deser(name, serializer, item):
        packed = serializer.serialize(item)
        unpacked = serializer.deserialize(packed)
        print("===== %s" % name)
        print(packed)
        print(item)
        print(unpacked)
        print(MapSerializer.extract_slot(item))
        print(MapSerializer.extract_slot(unpacked))
        assert MapSerializer.extract_slot(item) == MapSerializer.extract_slot(unpacked)
