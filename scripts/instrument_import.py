"""
Created on 10/24/16
Author = jchan
"""
__author__ = 'jchan'

import os
import csv
from algotrader.trading.ref_data import RefDataManager, \
    DBRefDataManager, Instrument, Currency, Exchange
from algotrader.trading.context import ApplicationConfig, ApplicationContext
from algotrader.utils.clock import Clock
import random
import time
from pymongo import MongoClient
from algotrader.config.app import ApplicationConfig
from algotrader.config.persistence import MongoDBConfig, PersistenceConfig
from algotrader.config.trading import BacktestingConfig
from algotrader.event.market_data import Bar
from algotrader.event.order import NewOrderRequest, OrdAction, OrdType
from algotrader.provider.persistence import DataStore, PersistenceMode
from algotrader.provider.persistence.mongodb import MongoDBDataStore
from algotrader.trading.account_mgr import AccountManager
from algotrader.trading.context import ApplicationContext
from algotrader.trading.portfolio import Portfolio
from algotrader.trading.seq_mgr import SequenceManager
from algotrader.utils.ser_deser import JsonSerializer, MapSerializer
from algotrader.trading.ref_data import Instrument


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

    # app_config = ApplicationConfig(None, None, None, persistence_config,
    #                                config)
    return ApplicationContext(app_config=app_config)



def setup_exchange_currency():
    context = get_default_app_context()
    client = MongoClient('localhost', 27017)

    store = context.provider_mgr.get(DataStore.Mongo)
    store.start(app_context=context)

    ref_data_mgr = context.ref_data_mgr
    ref_data_mgr.start(app_context=context)

    inst_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/refdata/instrument.csv'))
    ccy_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/refdata/ccy.csv'))
    exch_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/refdata/exch.csv'))

    with open(ccy_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print row
            ccy = Currency(ccy_id=row['ccy_id'], name=row['name'])
            if not isinstance(ccy, Currency) :
                print "%s is no currency" % ccy
            else:
                ref_data_mgr.add_ccy(ccy)


    with open(exch_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print row
            exch = Exchange(exch_id=row['exch_id'], name=row['name'])
            if not isinstance(exch, Exchange):
                print "%s is not exchange" % exch
            else:
                ref_data_mgr.add_exch(exch)

    ref_data_mgr.save_all()

def test_get():
    context = get_default_app_context()
    client = MongoClient('localhost', 27017)

    store = context.provider_mgr.get(DataStore.Mongo)
    store.start(app_context=context)

    ref_data_mgr = context.ref_data_mgr
    ref_data_mgr.start(app_context=context)

    print ref_data_mgr.get_inst(inst_id=0)
    print ref_data_mgr.get_ccy('AUD')

setup_exchange_currency()
test_get()

