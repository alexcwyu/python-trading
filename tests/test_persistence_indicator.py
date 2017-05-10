import math

from unittest import TestCase

from algotrader.technical.ma import SMA
from algotrader.trading.config import Config, load_from_yaml
from algotrader.trading.context import ApplicationContext

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
            load_from_yaml("../config/backtest.yaml"),
            load_from_yaml("../config/down2%.yaml"),
            test_override,
            {
                "Application": {
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

        bar = app_context.inst_data_mgr.get_series("bar")
        bar.start(app_context)

        sma = SMA(inputs=bar, input_keys='close', length=3)
        sma.start(app_context)

        t1 = 0
        t2 = t1 + 1
        t3 = t2 + 1
        t4 = t3 + 1
        t5 = t4 + 1

        bar.add(timestamp=t1, data={"close": 2.0, "open": 0})
        self.assertTrue(math.isnan(sma.now('value')))

        bar.add(timestamp=t2, data={"close": 2.4, "open": 1.4})
        self.assertTrue(math.isnan(sma.now('value')))

        bar.add(timestamp=t3, data={"close": 2.8, "open": 1.8})
        self.assertEquals(2.4, sma.now('value'))

        app_context.stop()

        ## restart...:

        app_context = self.create_app_context(conf={
            "Application": {
                "createDBAtStart": False,
                "deleteDBAtStop": True,
                "persistenceMode": "RealTime"
            }
        })
        app_context.start()

        bar_new = app_context.inst_data_mgr.get_series("bar")
        bar_new.start(app_context)

        sma_new = app_context.inst_data_mgr.get_series(sma.id())
        sma_new.start(app_context)

        bar_new.add(timestamp=t4, data={"close": 3.2, "open": 2.2})
        self.assertEquals(2.8, sma_new.now('value'))

        bar_new.add(timestamp=t5, data={"close": 3.6, "open": 2.6})
        self.assertEquals(3.2, sma_new.now('value'))

        self.assertTrue(math.isnan(sma_new.get_by_idx(0, 'value')))
        self.assertTrue(math.isnan(sma_new.get_by_idx(1, 'value')))
        self.assertEquals(2.4, sma_new.get_by_idx(2, 'value'))
        self.assertEquals(2.8, sma_new.get_by_idx(3, 'value'))
        self.assertEquals(3.2, sma_new.get_by_idx(4, 'value'))

        self.assertTrue(math.isnan(sma_new.get_by_time(t1, 'value')))
        self.assertTrue(math.isnan(sma_new.get_by_time(t2, 'value')))
        self.assertEquals(2.4, sma_new.get_by_time(t3, 'value'))
        self.assertEquals(2.8, sma_new.get_by_time(t4, 'value'))

        self.assertTrue(math.isnan(sma_new.get_by_time(t1, 'value')))
        self.assertTrue(math.isnan(sma_new.get_by_time(t1, 'value')))

        old_bar_dict = bar.get_data_dict(['close'])
        old_sma_dict = sma.get_data_dict(['value'])

        new_bar_dict = bar_new.get_data_dict(['close'])
        new_sma_dict = sma_new.get_data_dict(['value'])

        self.assertEquals(3, len(old_bar_dict))
        self.assertEquals(3, len(old_sma_dict))

        self.assertEquals(5, len(new_bar_dict))
        self.assertEquals(5, len(new_sma_dict))

        self.assertEquals(2.0, new_bar_dict[t1])
        self.assertTrue(math.isnan(new_sma_dict[t1]))

        self.assertEquals(2.4, new_bar_dict[t2])
        self.assertTrue(math.isnan(new_sma_dict[t2]))

        self.assertEquals(2.8, new_bar_dict[t3])
        self.assertEquals(2.4, new_sma_dict[t3])

        self.assertEquals(3.2, new_bar_dict[t4])
        self.assertEquals(2.8, new_sma_dict[t4])

        self.assertEquals(3.6, new_bar_dict[t5])
        self.assertEquals(3.2, new_sma_dict[t5])

        db = app_context.get_data_store()
        app_context.stop()
        db.remove_database()
