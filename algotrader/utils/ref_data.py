import csv

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
    if row['alt_symbols']:
        for item in row['alt_symbols'].split(";"):
            kv = item.split("=")
            alt_symbols[kv[0]] = kv[1]
    inst = ModelFactory.build_instrument(symbol=row['symbol'],
                                         type=row['type'],
                                         primary_exch_id=row['exch_id'],
                                         ccy_id=row['ccy_id'],
                                         name=row['name'],
                                         sector=row['sector'],
                                         industry=row['industry'],
                                         margin=row['margin'],
                                         alt_symbols=alt_symbols,
                                         underlying_ids=row['und_inst_id'],
                                         option_type=row['put_call'],
                                         strike=row['strike'],
                                         exp_date=row['expiry_date'],
                                         multiplier=row['factor'])
    data_store.save_instrument(inst)


def load_ccy_from_row(data_store, row):
    ccy = ModelFactory.build_currency(ccy_id=row['ccy_id'], name=row['name'])
    data_store.save_currency(ccy)


def load_exch_from_row(data_store, row):
    exch = ModelFactory.build_exchange(exch_id=row['exch_id'], name=row['name'])
    data_store.save_exchange(exch)
