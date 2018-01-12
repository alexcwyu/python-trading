
import math
from datetime import timedelta
from unittest import TestCase

import numpy as np

from algotrader.technical.function_wrapper import *
from algotrader.technical.historical_volatility import historical_volatility, historical_volatility_function
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext
from algotrader.utils.date import *

hv3 = periods_function(periods=3, name='hv3')(historical_volatility)

from tests import test_override

class IndicatorPersistenceTest(TestCase):
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
                    "dataStoreId": "Mongo",
                    "ceateAtStart": True,
                    "deleteDBAtStop": False,
                    "persistenceMode": "RealTime"
                }
            },
            conf
        ))

    def test_save_and_load_indicator(self):
        app_context = self.create_app_context(conf={
            "Application": {
                "createDBAtStart": True,
                "deleteDBAtStop": False,
                "persistenceMode": "RealTime"
            }
        })
        app_context.start()

        close = app_context.inst_data_mgr.get_series("close", df_id="TestBar", col_id="close", inst_id="test0001@TEST")
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

        ## restart...:

        # app_context = self.create_app_context(conf={
        #     "Application": {
        #         "createDBAtStart": False,
        #         "deleteDBAtStop": True,
        #         "persistenceMode": "RealTime"
        #     }
        # })
        # app_context.start()
        #
        # bar_new = app_context.inst_data_mgr.get_series("bar")
        # bar_new.start(app_context)
        #
        # sma_new = app_context.inst_data_mgr.get_series(sma.id())
        # sma_new.start(app_context)
        #
        # bar_new.add(timestamp=t4, data={"close": 3.2, "open": 2.2})
        # self.assertEquals(2.8, sma_new.now('value'))
        #
        # bar_new.add(timestamp=t5, data={"close": 3.6, "open": 2.6})
        # self.assertEquals(3.2, sma_new.now('value'))
        #
        # self.assertTrue(math.isnan(sma_new.get_by_idx(0, 'value')))
        # self.assertTrue(math.isnan(sma_new.get_by_idx(1, 'value')))
        # self.assertEquals(2.4, sma_new.get_by_idx(2, 'value'))
        # self.assertEquals(2.8, sma_new.get_by_idx(3, 'value'))
        # self.assertEquals(3.2, sma_new.get_by_idx(4, 'value'))
        #
        # self.assertTrue(math.isnan(sma_new.get_by_time(t1, 'value')))
        # self.assertTrue(math.isnan(sma_new.get_by_time(t2, 'value')))
        # self.assertEquals(2.4, sma_new.get_by_time(t3, 'value'))
        # self.assertEquals(2.8, sma_new.get_by_time(t4, 'value'))
        #
        # self.assertTrue(math.isnan(sma_new.get_by_time(t1, 'value')))
        # self.assertTrue(math.isnan(sma_new.get_by_time(t1, 'value')))
        #
        # old_bar_dict = bar.get_data_dict(['close'])
        # old_sma_dict = sma.get_data_dict(['value'])
        #
        # new_bar_dict = bar_new.get_data_dict(['close'])
        # new_sma_dict = sma_new.get_data_dict(['value'])
        #
        # self.assertEquals(3, len(old_bar_dict))
        # self.assertEquals(3, len(old_sma_dict))
        #
        # self.assertEquals(5, len(new_bar_dict))
        # self.assertEquals(5, len(new_sma_dict))
        #
        # self.assertEquals(2.0, new_bar_dict[t1])
        # self.assertTrue(math.isnan(new_sma_dict[t1]))
        #
        # self.assertEquals(2.4, new_bar_dict[t2])
        # self.assertTrue(math.isnan(new_sma_dict[t2]))
        #
        # self.assertEquals(2.8, new_bar_dict[t3])
        # self.assertEquals(2.4, new_sma_dict[t3])
        #
        # self.assertEquals(3.2, new_bar_dict[t4])
        # self.assertEquals(2.8, new_sma_dict[t4])
        #
        # self.assertEquals(3.6, new_bar_dict[t5])
        # self.assertEquals(3.2, new_sma_dict[t5])
        #
        # db = app_context.get_data_store()
        # app_context.stop()
        # db.remove_database()
