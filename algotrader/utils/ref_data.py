import csv

import pandas as pd

from algotrader.model.model_factory import ModelFactory


def get_inst_symbol(self, inst, provider_id):
    if inst:
        return inst.alt_symbols[provider_id] if provider_id in inst.alt_symbols else inst.symbol
    return None


def get_exch_id(self, exch, provider_id):
    if exch:
        return exch.alt_ids[provider_id] if provider_id in exch.alt_ids else exch.exch_id
    return None


def load_inst_from_csv(data_store, inst_file=None):
    if inst_file:
        with open(inst_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                load_inst_from_row(data_store, row)


def load_ccy_from_csv(data_store, ccy_file=None):
    if ccy_file:
        with open(ccy_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                load_ccy_from_row(data_store, row)


def load_exch_from_csv(data_store, exch_file=None):
    if exch_file:
        with open(exch_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                load_exch_from_row(data_store, row)


def load_inst_from_df(data_store, inst_df):
    for index, row in inst_df.iterrows():
        load_inst_from_row(data_store, row)


def load_ccy_from_df(data_store, ccy_df):
    for index, row in ccy_df.iterrows():
        load_ccy_from_row(data_store, row)


def load_exch_from_df(data_store, exch_df):
    for index, row in exch_df.iterrows():
        load_exch_from_row(data_store, row)


def load_inst_from_row(data_store, row):
    alt_symbols = {}
    if 'alt_symbols' in row and row['alt_symbols']:
        for item in row['alt_symbols'].split(";"):
            kv = item.split("=")
            alt_symbols[kv[0]] = kv[1]
    inst = ModelFactory.build_instrument(symbol=row['symbol'], inst_type=row['type'], primary_exch_id=row['exch_id'],
                                         ccy_id=row['ccy_id'], name=row['name'], sector=row['sector'],
                                         industry=row['industry'], margin=row['margin'], alt_symbols=alt_symbols,
                                         underlying_ids=row['und_inst_id'], option_type=row['put_call'],
                                         strike=row['strike'], exp_date=row['expiry_date'], multiplier=row['factor'])
    data_store.save_instrument(inst)


def load_ccy_from_row(data_store, row):
    ccy = ModelFactory.build_currency(ccy_id=row['ccy_id'], name=row['name'])
    data_store.save_currency(ccy)


def load_exch_from_row(data_store, row):
    alt_ids = {}
    if 'alt_ids' in row and row['alt_ids']:
        for item in row['alt_ids'].split(";"):
            kv = item.split("=")
            alt_ids[kv[0]] = kv[1]
    exch = ModelFactory.build_exchange(exch_id=row['exch_id'], name=row['name'], country_id=row['country_id'],
                                       trading_hours_id=row['trading_hours_id'],
                                       holidays_id=row['holidays_id'],
                                       alt_ids=alt_ids)
    data_store.save_exchange(exch)


def build_inst_dataframe_from_list(symbols, type='ETF', exch_id='NYSE', ccy_id='USD'):
    inst_df = pd.DataFrame({'name': symbols})
    inst_df['type'] = type
    inst_df['symbol'] = inst_df['name']
    inst_df['exch_id'] = exch_id
    inst_df['ccy_id'] = ccy_id
    inst_df['alt_symbol'] = ''
    inst_df['alt_exch_id'] = ''
    inst_df['sector'] = ''
    inst_df['industry'] = ''
    inst_df['put_call'] = ''
    inst_df['expiry_date'] = ''
    inst_df['und_inst_id'] = ''
    inst_df['factor'] = ''
    inst_df['strike'] = ''
    inst_df['margin'] = ''
    inst_df['inst_id'] = inst_df.index
    return inst_df


def representableAsInt(s: str):
    try:
        int(s)
        return True
    except ValueError:
        return False

