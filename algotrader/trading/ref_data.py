import abc
import csv

import os
from algotrader import Manager
from algotrader.provider.persistence import PersistenceMode

from algotrader.model.model_factory import ModelFactory
from algotrader.model.ref_data_pb2 import *


class RefDataManager(Manager):
    InMemory = "InMemory"
    DB = "DB"
    Mock = "Mock"

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(RefDataManager, self).__init__()

        self._inst_dict = {}
        self._ccy_dict = {}
        self._exch_dict = {}
        self._country_dict = {}

    def _start(self, app_context, **kwargs):
        self.seq_mgr = app_context.seq_mgr

    # add
    def add_inst(self, inst):
        if inst.inst_id in self._inst_dict:
            raise RuntimeError("duplicate inst, inst_id=%s, inst%s" % (inst.inst_id, self._inst_dict[inst.inst_id]))

        self._inst_dict[inst.inst_id] = inst

    def add_ccy(self, ccy):
        if ccy.ccy_id in self._ccy_dict:
            raise RuntimeError("duplicate ccy, ccy_id %s" % ccy.ccy_id)

        self._ccy_dict[ccy.ccy_id] = ccy

    def add_exch(self, exch):
        if exch.exch_id in self._exch_dict:
            raise RuntimeError("duplicate exch, exch_id %s" % exch.exch_id)

        self._exch_dict[exch.exch_id] = exch

    def add_country(self, country):
        if country.country_id in self._country_dict:
            raise RuntimeError("duplicate country, country_id %s" % country.country_id)

        self._country_dict[country.country_id] = country

    # get all
    def get_all_insts(self):
        return self._inst_dict.values()

    def get_all_ccys(self):
        return self._ccy_dict.values()

    def get_all_exchs(self):
        return self._exch_dict.values()

    def get_all_countries(self):
        return self._country_dict.values()

    # get
    def get_inst(self, inst_id):
        return self._inst_dict.get(inst_id, None)

    def get_ccy(self, ccy_id):
        return self._ccy_dict.get(ccy_id, None)

    def get_exch(self, exch_id):
        return self._exch_dict.get(exch_id, None)

    def get_country(self, country_id):
        return self._country_dict.get(country_id, None)

    # get inst
    def get_insts_by_ids(self, ids):
        ids = set(ids)
        return [self._inst_dict[id] for id in ids if id in self._inst_dict]

    def get_insts_by_symbols(self, symbols):
        symbols = set(symbols)
        return [inst for inst in self._inst_dict.values() if inst.symbol in symbols]

    # create inst
    def create_inst(self, name, type, symbol, exch_id, ccy_id, alt_symbols=None,
                    sector=None, industry=None,
                    put_call=None, expiry_date=None, und_inst_id=None, factor=1, strike=0.0, margin=0.0):
        inst_id = self.seq_mgr.get_next_sequence("instruments")
        inst = ModelFactory.build_instrument(inst_id=inst_id, name=name, type=type,
                                             symbol=symbol,
                                             exch_id=exch_id, ccy_id=ccy_id,
                                             alt_symbols=alt_symbols, sector=sector, industry=industry,
                                             put_call=put_call,
                                             expiry_date=expiry_date, und_inst_id=und_inst_id, factor=factor,
                                             strike=strike, margin=margin)
        self.add_inst(inst)

    #

    def get_symbol(self, inst_id, provider_id):
        if self.alt_symbols and provider_id in self.alt_symbols:
            return self.alt_symbols[provider_id]
        return self.symbol

    def get_exch_id(self, inst_id, provider_id):
        if self.alt_exch_id and provider_id in self.alt_exch_id:
            return self.alt_exch_id[provider_id]
        return self.exch_id

    def get_ccy_id(self, inst_id, provider_id):
        pass


class DBRefDataManager(RefDataManager):
    def __init__(self):
        super(DBRefDataManager, self).__init__()

    def _start(self, app_context, **kwargs):
        super(DBRefDataManager, self)._start(app_context, **kwargs)
        self.store = self.app_context.get_data_store()
        self.persist_mode = self.app_context.app_config.get_app_config("persistenceMode")
        self.load_all()

    def _stop(self):
        self.save_all()
        self.reset()

    def load_all(self):
        if hasattr(self, "store") and self.store:
            self.store.start(self.app_context)
            for inst in self.store.load_all('instruments'):
                self._inst_dict[inst.inst_id] = inst
            for ccy in self.store.load_all('currencies'):
                self._ccy_dict[ccy.ccy_id] = ccy
            for exch in self.store.load_all('exchanges'):
                self._exch_dict[exch.exch_id] = exch

    def save_all(self):
        if hasattr(self, "store") and self.store and self.persist_mode != PersistenceMode.Disable:
            for inst in self._inst_dict.values():
                self.store.save_instrument(inst)
            for ccy in self._ccy_dict.values():
                self.store.save_currency(ccy)
            for exch in self._exch_dict.values():
                self.store.save_exchange(exch)

    def reset(self):
        self._inst_dict = {}
        self._inst_symbol_dict = {}
        self._ccy_dict = {}
        self._exch_dict = {}

    def add_inst(self, inst):
        super(DBRefDataManager, self).add_inst(inst)
        if hasattr(self, "store") and self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_instrument(inst)

    def add_ccy(self, ccy):
        super(DBRefDataManager, self).add_ccy(ccy)
        if hasattr(self, "store") and self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_currency(ccy)

    def add_exch(self, exch):
        super(DBRefDataManager, self).add_exch(exch)
        if hasattr(self, "store") and self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_exchange(exch)

    def id(self):
        raise RefDataManager.DB


class InMemoryRefDataManager(RefDataManager):
    def __init__(self):
        super(InMemoryRefDataManager, self).__init__()

    def _start(self, app_context, **kwargs):
        self.inst_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/refdata/instrument.csv'))
        self.ccy_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/refdata/ccy.csv'))
        self.exch_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/refdata/exch.csv'))
        self.country_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/refdata/country.csv'))

        self.load_all()

    def _stop(self):
        pass

    def load_all(self):
        with open(self.inst_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

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
                                                     option_style=Instrument.European,
                                                     strike=row['strike'],
                                                     exp_date=row['expiry_date'],
                                                     multiplier=row['factor'])
                self.add_inst(inst)

        with open(self.ccy_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                #
                # alt_code = {}
                # if 'alt_code' in row:
                #     for item in row['alt_code'].split(";"):
                #         kv = item.split("=")
                #         alt_code[kv[0]] = kv[1]

                ccy = ModelFactory.build_currency(ccy_id=row['ccy_id'], name=row['name'])
                self.add_ccy(ccy)

        with open(self.exch_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                alt_ids = {}
                if 'alt_code' in row:
                    for item in row['alt_code'].split(";"):
                        kv = item.split("=")
                        alt_ids[kv[0]] = kv[1]

                exch = ModelFactory.build_exchange(exch_id=row['exch_id'], name=row['name'],
                                                   alt_ids=alt_ids)
                self.add_exch(exch)

    def save_all(self):
        pass

    def id(self):
        raise RefDataManager.InMemory
