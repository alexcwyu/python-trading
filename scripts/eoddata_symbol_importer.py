from gevent import monkey
# monkey.patch_all(Event=True)


import re
from scripts.ib_inst_utils import init_ib, import_inst_from_ib, app_context
import time
import logging
from algotrader.utils import logger
from algotrader.provider.persistence import PersistenceMode
from algotrader.provider.persistence.data_store import DataStore
from algotrader.trading.context import ApplicationContext
from pymongo import MongoClient
from algotrader.config.app import ApplicationConfig
from algotrader.config.persistence import MongoDBConfig, PersistenceConfig
from algotrader.trading.ref_data import RefDataManager
from algotrader.utils.clock import Clock

logger.setLevel(logging.DEBUG)
#file_name = '../data/refdata/eoddata/HKEX.txt'
arca = '../data/refdata/eoddata/AMEX.txt'
sehk = '../data/refdata/eoddata/HKEX.txt'
nasdaq = '../data/refdata/eoddata/NASDAQ.txt'
nyse = '../data/refdata/eoddata/NYSE.txt'


app_context = app_context()
broker = init_ib(app_context)

def get_default_app_context():
    config = MongoDBConfig()
    persistence_config = PersistenceConfig(None,
                                           DataStore.Mongo, PersistenceMode.RealTime,
                                           DataStore.Mongo, PersistenceMode.RealTime,
                                           DataStore.Mongo, PersistenceMode.RealTime,
                                           DataStore.Mongo, PersistenceMode.RealTime)

    app_config = ApplicationConfig("InstrumentImport",
                                   RefDataManager.DB,
                                   Clock.Simulation,
                                   persistence_config,
                                   config)

    return ApplicationContext(app_config=app_config)



context = get_default_app_context()
client = MongoClient('localhost', 27017)

store = context.provider_mgr.get(DataStore.Mongo)
store.start(app_context=context)

ref_data_mgr = context.ref_data_mgr
ref_data_mgr.start(app_context=context)

def read_eod_and_import(file_name, exchange, ccy = 'USD'):
    with open(file_name) as f:
        for line in f:
            tokens = re.split('\t', line)
            sym = tokens[0]
            if ref_data_mgr.get_inst(symbol=sym) is None:
                import_inst_from_ib(broker=broker, symbol=str(tokens[0]), exchange=exchange, currency=ccy)



read_eod_and_import(sehk, 'SEHK', 'HKD')
# read_eod_and_import(arca, 'ARCA', 'USD')
# read_eod_and_import(nasdaq, 'NASDAQ', 'USD')
#read_eod_and_import(nyse, 'NYSE', 'USD')


# import_inst_from_ib(broker=broker, symbol='VXX', exchange='ARCA', currency='USD')

# for inst in app_context.ref_data_mgr.get_all_insts():
#     print inst