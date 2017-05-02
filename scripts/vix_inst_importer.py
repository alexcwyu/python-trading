"""
Created on 10/24/16
Author = jchan
"""
__author__ = 'jchan'

import os
import csv
import datetime
from algotrader.trading.ref_data import RefDataManager, \
    Instrument, Currency, Exchange, InstType
from algotrader.trading.clock import Clock
import random
import time
from pymongo import MongoClient
from algotrader.config.app import ApplicationConfig
from algotrader.config.persistence import MongoDBConfig, PersistenceConfig
# from algotrader.config.trading import BacktestingConfig
from algotrader.provider.persistence import PersistenceMode
from algotrader.provider.persistence.data_store import DataStore
from algotrader.provider.persistence.mongodb import MongoDBDataStore
from algotrader.trading.context import ApplicationContext
from algotrader.trading.portfolio import Portfolio
from algotrader.trading.seq_mgr import SequenceManager
from algotrader.provider.feed import Feed

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

# source: http://www.macroption.com/vix-expiration-calendar/
vix_expiries = ['19 May 2004', '16 June 2004', '14 July 2004', '18 August 2004', '15 September 2004', \
     '13 October 2004', '17 November 2004', '19 January 2005', '16 February 2005', '16 March 2005', \
     '18 May 2005', '15 June 2005', '17 August 2005', '19 October 2005', '16 November 2005', '21 December 2005', '18 January 2006', \
     '15 February 2006', '22 March 2006', '19 April 2006', '17 May 2006', '21 June 2006', '19 July 2006', '16 August 2006', \
     '20 September 2006', '18 October 2006', '15 November 2006', '20 December 2006', '17 January 2007', '14 February 2007', \
     '21 March 2007', '18 April 2007', '16 May 2007', '20 June 2007', '18 July 2007', '22 August 2007', '19 September 2007', \
     '17 October 2007', '21 November 2007', '19 December 2007', '16 January 2008', '19 February 2008', '19 March 2008', \
     '16 April 2008', '21 May 2008', '18 June 2008', '16 July 2008', '20 August 2008', '17 September 2008', '22 October 2008', \
     '19 November 2008', '17 December 2008', '21 January 2009', '18 February 2009', '18 March 2009', '15 April 2009', \
     '20 May 2009', '17 June 2009', '22 July 2009', '19 August 2009', '16 September 2009', '21 October 2009', \
     '18 November 2009', '16 December 2009', '20 January 2010', '17 February 2010', '17 March 2010', '21 April 2010',\
     '19 May 2010', '16 June 2010', '21 July 2010', '18 August 2010', '15 September 2010', '20 October 2010', \
     '17 November 2010', '22 December 2010', '19 January 2011', '16 February 2011', '16 March 2011', '20 April 2011', \
     '18 May 2011', '15 June 2011', '20 July 2011', '17 August 2011', '21 September 2011', '19 October 2011',\
     '16 November 2011', '21 December 2011', '18 January 2012', '15 February 2012', '21 March 2012', '18 April 2012',\
     '16 May 2012', '20 June 2012', '18 July 2012', '22 August 2012', '19 September 2012', '17 October 2012', \
     '21 November 2012', '19 December 2012', '16 January 2013', '13 February 2013', '20 March 2013', '17 April 2013', \
     '22 May 2013', '19 June 2013', '17 July 2013', '21 August 2013', '18 September 2013', '16 October 2013', \
     '20 November 2013', '18 December 2013', '22 January 2014', '19 February 2014', '18 March 2014', '16 April 2014', \
     '21 May 2014', '18 June 2014', '16 July 2014', '20 August 2014', '17 September 2014', '22 October 2014', \
     '19 November 2014', '17 December 2014', '21 January 2015', '18 February 2015', '18 March 2015', '15 April 2015', \
     '20 May 2015', '17 June 2015', '22 July 2015', '19 August 2015', '16 September 2015', '21 October 2015', \
     '18 November 2015', '16 December 2015', '20 January 2016', '17 February 2016', '16 March 2016', '20 April 2016', \
     '18 May 2016', '15 June 2016', '20 July 2016', '17 August 2016', '21 September 2016', '19 October 2016', \
     '16 November 2016', '21 December 2016', '18 January 2017', '15 February 2017', '22 March 2017', '19 April 2017', \
     '17 May 2017', '21 June 2017', '19 July 2017', '16 August 2017', '20 September 2017', '18 October 2017', \
     '15 November 2017', '20 December 2017']

future_code = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
month_code_dict = dict(zip(range(1,13), future_code))

def build_vix_future(expiry_date_str, seq_mgr):
    import re
    expiry_date = datetime.datetime.strptime(expiry_date_str, '%d %B %Y')
    tokens = re.split(' ', expiry_date_str)
    inst_id = seq_mgr.get_next_sequence("instruments")
    symbol = 'VX%s%s' % (month_code_dict[expiry_date.month], expiry_date.year)
    return Instrument(inst_id, "VIX Future %s %s" % (tokens[1], tokens[2]), type=InstType.Future,
                      symbol=symbol,
                      exch_id='CBOE', ccy_id='USD',
                      alt_symbols={"Quandl": "CBOE/%s" % symbol, "IB": "VIX"}, expiry_date=expiry_date, factor=1000)




def import_vix_future():
    context = get_default_app_context()
    client = MongoClient('localhost', 27017)

    store = context.provider_mgr.get(DataStore.Mongo)
    store.start(app_context=context)

    ref_data_mgr = context.ref_data_mgr
    ref_data_mgr.start(app_context=context)

    seq_mgr = SequenceManager()
    seq_mgr.start(app_context=context)

    for ex in vix_expiries:
        inst = build_vix_future(ex, seq_mgr)
        ref_data_mgr.add_inst(inst)
    ref_data_mgr.save_all()


setup_exchange_currency()
test_get()

import_vix_future()
