from unittest import TestCase

import math
import numpy as np
from datetime import timedelta
from algotrader.technical.function_wrapper import *
from algotrader.technical.historical_volatility import hvol30
from algotrader.trading.context import ApplicationContext
from algotrader.utils.date import *
from algotrader.technical.function_wrapper import *
from algotrader.technical.historical_volatility import historical_volatility, historical_volatility_function
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from algotrader.utils.date import *
from tests import test_override

hv3 = periods_function(periods=3, name='hv3')(historical_volatility)


def average(arr: np.ndarray):
    return np.average(arr)

avg1 = periods_function(periods=1, name='avg1')(average)
avg2 = periods_function(periods=2, name='avg2')(average)
avg3 = periods_function(periods=3, name='avg3')(average)


class IndicatorTest(TestCase):
    stg_override = {
        "Strategy": {
            "down2%": {
                "qty": 1000
            }
        }
    }

    def create_app_context(self, conf):
        return ApplicationContext(config=Config(
            load_from_yaml("../config/unittest.yaml"),
            load_from_yaml("../config/down2%.yaml"),
            test_override,
            {
                "Application": {
                    "dataStoreId": "InMemory",
                    "ceateAtStart": True,
                    "deleteDBAtStop": False,
                    "persistenceMode": "RealTime"
                }
            },
            conf
        ))

    def test_update_series(self):

        app_context = self.create_app_context(conf={
            "Application": {
                "createDBAtStart": True,
                "deleteDBAtStop": False,
                "persistenceMode": "RealTime"
            }
        })
        app_context.start()

        close = app_context.inst_data_mgr.get_series("close", df_id="TestBar", col_id="close", inst_id="test0001@TEST", transient=True)
        close.start(app_context)

        hv3_series = hv3 * close
        hv3_series.start(app_context)

        t1 = datetime.datetime(2001, 1, 1, 10, 30, 0)
        t2 = t1 + timedelta(seconds=30)
        t3 = t2 + timedelta(seconds=30)
        t4 = t3 + timedelta(seconds=30)
        t5 = t4 + timedelta(seconds=30)

        close.add(timestamp=datetime_to_unixtimemillis(t1), value=100.0)
        self.assertTrue(math.isnan(hv3_series.tail(1).data[0]))

        close.add(timestamp=datetime_to_unixtimemillis(t2), value=103.0)
        self.assertTrue(math.isnan(hv3_series.tail(1).data[0]))

        close.add(timestamp=datetime_to_unixtimemillis(t3), value=101.0)
        self.assertAlmostEqual(historical_volatility_function(np.array([100.0, 103.0, 101.0])), hv3_series.tail(1).data[0], places=0.000001)

        close.add(timestamp=datetime_to_unixtimemillis(t4), value=99.0)
        self.assertAlmostEqual(historical_volatility_function(np.array([103.0, 101.0, 99.0])), hv3_series.tail(1).data[0], places=0.000001)

        close.add(timestamp=datetime_to_unixtimemillis(t5), value=97.0)
        self.assertAlmostEqual(historical_volatility_function(np.array([101.0, 99.0, 97.0])), hv3_series.tail(1).data[0], places=0.000001)


        app_context.stop()

    # def test_reuse(self):
    #     close = self.app_context.inst_data_mgr.get_series("bar")
    #     close.start(self.app_context)
    #
    #     hvol30_series = hvol30 * close

        #
        # sma1 = get_or_create_indicator(self.app_context.inst_data_mgr, cls=SMA, inputs='bar', input_keys='close',
        #                                length=3)
        # sma1.start(self.app_context)
        #
        # sma2 = get_or_create_indicator(self.app_context.inst_data_mgr, cls=SMA, inputs='bar', input_keys='close',
        #                                length=3)
        # sma2.start(self.app_context)
        #
        # sma3 = get_or_create_indicator(self.app_context.inst_data_mgr, cls=SMA, inputs='bar', input_keys='close',
        #                                length=10)
        # sma3.start(self.app_context)
        #
        # self.assertEquals(sma1, sma2)
        # self.assertNotEquals(sma2, sma3)
        # self.assertNotEquals(sma1, sma3)
        #
        # sma4 = get_or_create_indicator(self.app_context.inst_data_mgr, cls=SMA, inputs=sma3, length=10)
        # sma4.start(self.app_context)
        #
        # self.assertEquals(sma4.input_series[0], sma3)

    # def test_parse(self):
    #     bar = parse_series(self.app_context.inst_data_mgr, "bar")
    #     bar.start(self.app_context)
    #
    #     sma1 = parse_series(self.app_context.inst_data_mgr, "SMA(bar[close],length=3)")
    #     sma1.start(self.app_context)
    #
    #     sma2 = parse_series(self.app_context.inst_data_mgr, "SMA(SMA(bar[close],length=3)[value],length=10)")
    #     sma2.start(self.app_context)
    #
    #     rsi = parse_series(self.app_context.inst_data_mgr, "RSI(SMA(SMA('bar',close,3),value,10),value,14, 9)")
    #     rsi.start(self.app_context)
    #
    #     self.assertEquals(sma1.input, bar)
    #     self.assertEquals(3, sma1.length)
    #
    #     self.assertEquals(sma2.input, sma1)
    #     self.assertEquals(10, sma2.length)
    #
    #     self.assertEquals(rsi.input, sma2)
    #     self.assertEquals(14, rsi.length)
    #
    # def test_fail_parse(self):
    #     with self.assertRaises(AssertionError):
    #         parse_series(self.app_context.inst_data_mgr, "SMA('Bar.Close',3")
    #
    #     with self.assertRaises(AssertionError):
    #         parse_series(self.app_context.inst_data_mgr, "RSI(SMA(SMA('Bar.Close',3,10),14)")
