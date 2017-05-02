from gevent import monkey
from gevent.event import AsyncResult

monkey.patch_all()

from algotrader.config.app import ApplicationConfig
from algotrader.config.broker import IBConfig
from algotrader.config.persistence import MongoDBConfig
from algotrader.config.persistence import PersistenceConfig
from algotrader.provider.broker import Broker
from algotrader.provider.persistence import PersistenceMode
from algotrader.provider.persistence.data_store import DataStore
from algotrader.trading.context import ApplicationContext
from algotrader.trading.ref_data import RefDataManager
from algotrader.trading.clock import Clock
from algotrader.utils import logger


def app_context():
    persistence_config = PersistenceConfig(None,
                                           DataStore.Mongo, PersistenceMode.RealTime,
                                           DataStore.Mongo, PersistenceMode.RealTime,
                                           DataStore.Mongo, PersistenceMode.RealTime,
                                           DataStore.Mongo, PersistenceMode.RealTime)
    app_config = ApplicationConfig(id=None, ref_data_mgr_type=RefDataManager.DB, clock_type=Clock.RealTime,
                                   persistence_config=persistence_config,
                                   provider_configs=[MongoDBConfig(), IBConfig(client_id=2, use_gevent=True)])
    app_context = ApplicationContext(app_config=app_config)

    return app_context

def init_ib(app_context):

    app_context.start()
    broker = app_context.provider_mgr.get(Broker.IB)
    broker.start(app_context)
    return broker



def import_inst_from_ib(broker, symbol, sec_type='STK', exchange=None, currency=None):
    try:
        result = AsyncResult()
        logger.info("importing symbol %s" % symbol)
        broker.reqContractDetails(symbol=symbol, sec_type=sec_type, exchange=exchange, currency=currency, callback=result)
        # broker.reqScannerSubscription(inst_type='STK', location_code='STK.US', scan_code='TOP_PERC_GAIN', above_vol=1000000, callback=callback)

        logger.info("done %s %s" % (symbol, result.get(timeout=3)))
    except Exception as e:
        logger.error("faile to import %s", symbol, e)



