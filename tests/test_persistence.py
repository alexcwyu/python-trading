import math
from unittest import TestCase

from algotrader.provider.persistence import DataStore, PersistenceMode
from algotrader.config.persistence import PersistenceConfig
from algotrader.config.app import ApplicationConfig
from algotrader.provider.persistence import DataStore
from algotrader.technical.ma import SMA
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock


class PersistenceTest(TestCase):
    def new_app_context(self):
        app_config = ApplicationConfig(persistence_config = PersistenceConfig(
            ref_ds_id=DataStore.InMemoryDB, ref_persist_mode=PersistenceMode.RealTime,
            trade_ds_id=DataStore.InMemoryDB, trade_persist_mode=PersistenceMode.RealTime,
            ts_ds_id=DataStore.InMemoryDB, ts_persist_mode=PersistenceMode.RealTime,
            seq_ds_id=DataStore.InMemoryDB, seq_persist_mode=PersistenceMode.RealTime))
        app_context = ApplicationContext(app_config=app_config)
        app_context.start()
        return app_context

    def test_save_and_load_indicator(self):
        app_context = self.new_app_context()

        bar = app_context.inst_data_mgr.get_series("bar")
        bar.start(app_context)

        sma = SMA(bar, input_key='close', length=3)
        sma.start(app_context)

        t1 = 0
        t2 = t1 + 1
        t3 = t2 + 1
        t4 = t3 + 1
        t5 = t4 + 1

        bar.add({"timestamp": t1, "close": 2.0, "open": 0})
        self.assertTrue(math.isnan(sma.now('value')))

        bar.add({"timestamp": t2, "close": 2.4, "open": 1.4})
        self.assertTrue(math.isnan(sma.now('value')))

        bar.add({"timestamp": t3, "close": 2.8, "open": 1.8})
        self.assertEquals(2.4, sma.now('value'))

        app_context.stop()

        ## restart...:

        app_context = self.new_app_context()

        bar_new = app_context.inst_data_mgr.get_series("bar")
        bar_new.start(app_context)

        sma_new = app_context.inst_data_mgr.get_series(sma.id())
        sma_new.start(app_context)

        bar_new.add({"timestamp": t4, "close": 3.2, "open": 2.2})
        self.assertEquals(2.8, sma_new.now('value'))

        bar_new.add({"timestamp": t5, "close": 3.6, "open": 2.6})
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

        self.assertEquals(2.0, new_bar_dict['0'])
        self.assertTrue(math.isnan(new_sma_dict['0']))

        self.assertEquals(2.4, new_bar_dict['1'])
        self.assertTrue(math.isnan(new_sma_dict['1']))

        self.assertEquals(2.8, new_bar_dict['2'])
        self.assertEquals(2.4, new_sma_dict['2'])

        self.assertEquals(3.2, new_bar_dict['3'])
        self.assertEquals(2.8, new_sma_dict['3'])

        self.assertEquals(3.6, new_bar_dict['4'])
        self.assertEquals(3.2, new_sma_dict['4'])

        db = app_context.get_ref_data_store()
        app_context.stop()
        db.delete_db()
