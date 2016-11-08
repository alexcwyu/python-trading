import abc
import csv
import os

from algotrader import HasId
from algotrader import Manager
from algotrader.config.persistence import PersistenceMode
from algotrader.provider.persistence import Persistable
from algotrader.utils.ser_deser import Serializable


class ReferenceData(Persistable):
    pass


class InstType:
    Stock = 'STK'
    Future = 'FUT'
    Option = 'OPT'
    FutureOption = 'FOT'
    Index = 'IDX'
    CASH = 'CASH'
    ETF = 'ETF'
    Combo = 'CBO'


class CallPut:
    Call = "C"
    Put = "P"


class HolidayImpactType:
    FullDay = 'Full Day'
    Replace = 'Replace'
    EarlyClose = 'Early Close'
    LateOpen = 'Late Open'
    Modify = 'Modify'


class Instrument(ReferenceData):
    __slots__ = (
        'id',
        'name',
        'type',
        'symbol',
        'primary_exch_id',
        'exch_ids',
        'ccy_id',
        'alt_symbols',
        'sector',
        'industry',
        'und_inst_id',
        'expiry_date',
        'put_call',
        'factor',
        'strike',
        'margin',
        'tick_size',
        'trading_hours_id',
        'holidays_id',
    )

    def __init__(self, id=None, name=None, type=None, symbol=None, primary_exch_id=None, exch_ids=None, ccy_id=None,
                 alt_symbols=None,
                 sector=None, industry=None,
                 und_inst_id=None, expiry_date=None, put_call=None, factor=1, strike=0.0, margin=0.0, tick_size=0.0001,
                 trading_hours_id=None, holidays_id=None):
        self.id = id
        self.name = name
        self.type = type
        self.symbol = symbol
        self.exch_ids = exch_ids if exch_ids else []
        self.ccy_id = ccy_id
        self.alt_symbols = alt_symbols if alt_symbols else {}

        self.sector = sector
        self.industry = industry

        self.und_inst_id = und_inst_id
        self.expiry_date = expiry_date
        self.put_call = put_call

        self.factor = float(factor) if factor else 1
        self.strike = float(strike) if strike else 0.0
        self.margin = float(margin) if margin else 0.0
        self.tick_size = float(tick_size) if tick_size else 0.0001

        self.trading_hours_id = trading_hours_id
        self.holidays_id = holidays_id


    def id(self):
        return self.id



class Exchange(ReferenceData):
    __slots__ = (
        'id',
        'code',
        'name',
        'country_id',
        'alt_codes',
        'trading_hours'
    )

    def __init__(self, id=None, code=None, name=None, country_id=None, alt_codes=None):
        self.id = id
        self.code = code
        self.name = name
        self.country_id = country_id
        self.alt_codes = alt_codes if alt_codes else {}

    def id(self):
        return self.id

    def get_code(self, provider_id):
        if self.alt_codes and provider_id in self.alt_codes:
            return self.alt_codes[provider_id]
        return self.code


class Country(ReferenceData):
    _slots__ = (
        'id',
        'code',
        'name',
    )

    def __init__(self, id=None, code=None, name=None):
        self.id = id
        self.code = code
        self.name = name

    def id(self):
        return self.id


class Currency(ReferenceData):
    __slots__ = (
        'id',
        'code',
        'name',
        'alt_codes'
    )

    def __init__(self, id=None, code=None, name=None, alt_codes=None):
        self.id = id
        self.code = code
        self.name = name
        self.alt_codes = alt_codes if alt_codes else {}

    def id(self):
        return self.id

    def get_code(self, provider_id):
        if self.alt_codes and provider_id in self.alt_codes:
            return self.alt_codes[provider_id]
        return self.id


class Holiday(Serializable):
    __slots__ = (
        'trading_date',
        'start_date',
        'start_time',
        'end_date',
        'end_time',
        'impact_type',
        'desc'
    )

    def __init__(self,
                 trading_date=None, start_date=None, start_time=None, end_date=None, end_time=None, impact_type=None,
                 desc=None):
        self.trading_date = trading_date
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time
        self.impact_type = impact_type
        self.desc = desc


class TradingHolidays(ReferenceData):
    __slots__ = (
        'id',
        'holidays',
    )

    def __init__(self,
                 # holidays_id=None,
                 id=None, holidays=None):
        self.id = id
        self.holidays = holidays

    def id(self):
        return self.id


class TradingSession(Serializable):
    __slots__ = (
        'start_date',
        'start_time',
        'end_date',
        'end_time',
        'eod',
    )

    def __init__(self,
                 # holidays_id=None,
                 start_date=None, start_time=None,
                 end_date=None, end_time=None,
                 eod=None):
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time
        self.eod = eod


class TradingHours(ReferenceData):
    __slots__ = (
        'id',
        'name',
        'timezone',
        'sessions',
    )

    def __init__(self,
                 id=None,
                 name=None,
                 timezone=None,
                 sessions=None):
        self.id = id
        self.name = name
        self.timezone = timezone
        self.sessions = sessions

    def id(self):
        return self.id


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
        return [self._inst_dict[id] for id in ids if id in self.self._inst_dict]

    def get_insts_by_symbols(self, symbols):
        symbols = set(symbols)
        return [inst for inst in self._inst_dict.itervalues() if inst.symbol in symbols]

    # create inst
    def create_inst(self, name, type, symbol, exch_id, ccy_id, alt_symbols=None,
                    sector=None, industry=None,
                    put_call=None, expiry_date=None, und_inst_id=None, factor=1, strike=0.0, margin=0.0):
        inst_id = self.seq_mgr.get_next_sequence("instruments")
        inst = Instrument(inst_id=inst_id, name=name, type=type,
                          symbol=symbol,
                          exch_id=exch_id, ccy_id=ccy_id,
                          alt_symbols=alt_symbols, sector=sector, industry=industry,
                          put_call=put_call,
                          expiry_date=expiry_date, und_inst_id=und_inst_id, factor=factor, strike=strike, margin=margin)
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


class DBRefDataManager(RefDataManager):
    def __init__(self):
        super(DBRefDataManager, self).__init__()

    def _start(self, app_context, **kwargs):
        super(DBRefDataManager, self)._start(app_context, **kwargs)
        self.store = self.app_context.get_ref_data_store()
        self.persist_mode = self.app_context.app_config.persistence_config.ref_persist_mode
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

                inst = Instrument(inst_id=row['inst_id'], name=row['name'], type=row['type'], symbol=row['symbol'],
                                  exch_id=row['exch_id'], ccy_id=row['ccy_id'], alt_symbols=alt_symbols,
                                  sector=row['sector'], industry=row['industry'],
                                  put_call=row['put_call'], expiry_date=row['expiry_date'],
                                  und_inst_id=row['und_inst_id'],
                                  factor=row['factor'], strike=row['strike'], margin=row['margin'])
                self.add_inst(inst)

        with open(self.ccy_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                alt_code = {}
                if row['alt_code']:
                    for item in row['alt_code'].split(";"):
                        kv = item.split("=")
                        alt_code[kv[0]] = kv[1]

                ccy = Currency(ccy_id=row['ccy_id'], code=['code'], name=row['name'], alt_code=alt_code)
                self.add_ccy(ccy)

        with open(self.exch_file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                alt_code = {}
                if row['alt_code']:
                    for item in row['alt_code'].split(";"):
                        kv = item.split("=")
                        alt_code[kv[0]] = kv[1]

                exch = Exchange(exch_id=row['exch_id'], code=['code'], name=row['name'], alt_code=alt_code)
                self.add_exch(exch)

    def save_all(self):
        pass

    def id(self):
        raise RefDataManager.InMemory
