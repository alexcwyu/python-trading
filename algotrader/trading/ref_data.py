from algotrader import Manager, Context
from algotrader.provider.datastore import PersistenceMode

from algotrader.model.ref_data_pb2 import *

class RefDataManager(Manager):
    def __init__(self):
        super(RefDataManager, self).__init__()

        self._inst_dict = {}
        self._ccy_dict = {}
        self._exch_dict = {}
        self.store = None

    def _start(self, app_context: Context) -> None:
        self.store = self.app_context.get_data_store()
        self.persist_mode = self.app_context.config.get_app_config("persistenceMode")
        self.load_all()

    def _stop(self):
        self.save_all()
        self.reset()

    def load_all(self):
        if self.store:
            self.store.start(self.app_context)
            for inst in self.store.load_all(Instrument):
                self._inst_dict[inst.inst_id] = inst
            for ccy in self.store.load_all(Currency):
                self._ccy_dict[ccy.ccy_id] = ccy
            for exch in self.store.load_all(Exchange):
                self._exch_dict[exch.exch_id] = exch

    def save_all(self):
        if self.store and self.persist_mode != PersistenceMode.Disable:
            for inst in self._inst_dict.values():
                self.store.save_instrument(inst)
            for ccy in self._ccy_dict.values():
                self.store.save_currency(ccy)
            for exch in self._exch_dict.values():
                self.store.save_exchange(exch)

    def reset(self):
        self._inst_dict = {}
        self._ccy_dict = {}
        self._exch_dict = {}

    # get all
    def get_all_insts(self):
        return self._inst_dict.values()

    def get_all_ccys(self):
        return self._ccy_dict.values()

    def get_all_exchs(self):
        return self._exch_dict.values()

    def get_inst(self, inst_id):
        return self._inst_dict.get(inst_id, None)

    def get_ccy(self, ccy_id):
        return self._ccy_dict.get(ccy_id, None)

    def get_exch(self, exch_id):
        return self._exch_dict.get(exch_id, None)

    def get_insts_by_ids(self, ids):
        ids = set(ids)
        return [self._inst_dict[id] for id in ids if id in self._inst_dict]

    def get_insts_by_symbols(self, symbols):
        symbols = set(symbols)
        return [inst for inst in self._inst_dict.values() if inst.symbol in symbols]

    def add_inst(self, inst):
        self._inst_dict[inst.inst_id] = inst
        if self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_instrument(inst)

    def add_ccy(self, ccy):
        self._ccy_dict[ccy.ccy_id] = ccy
        if self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_currency(ccy)

    def add_exch(self, exch):
        self._exch_dict[exch.exch_id] = exch
        if self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_exchange(exch)

    def id(self):
        raise "RefDataManager"
