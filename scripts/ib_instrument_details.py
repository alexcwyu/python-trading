from gevent import monkey

monkey.patch_all()

import time
from algotrader.config.app import ApplicationConfig
from algotrader.config.broker import IBConfig
from algotrader.config.persistence import MongoDBConfig
from algotrader.config.persistence import PersistenceConfig
from algotrader.provider.broker import Broker
from algotrader.provider.persistence import PersistenceMode
from algotrader.provider.persistence.data_store import DataStore
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock
import threading

persistence_config = PersistenceConfig(None,
                                       DataStore.InMemoryDB, PersistenceMode.RealTime,
                                       DataStore.InMemoryDB, PersistenceMode.RealTime,
                                       DataStore.InMemoryDB, PersistenceMode.RealTime,
                                       DataStore.InMemoryDB, PersistenceMode.RealTime)
app_config = ApplicationConfig(id=None, ref_data_mgr_type=RefDataManager.InMemory, clock_type=Clock.RealTime,
                               persistence_config=persistence_config,
                               provider_configs=[MongoDBConfig(), IBConfig(client_id=2, use_gevent=True)])
app_context = ApplicationContext(app_config=app_config)

app_context.start()
broker = app_context.provider_mgr.get(Broker.IB)
broker.start(app_context)


event = threading.Event()
callback = lambda: event.set()

#broker.reqContractDetails(symbol='1', sec_type='STK', exchange="SEHK", currency="HKD", callback=callback)
broker.reqScannerSubscription(inst_type='STK', location_code='STK.US', scan_code='TOP_PERC_GAIN', above_vol=1000000, callback=callback)

event.wait()

print "done"