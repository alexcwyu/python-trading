import abc
import csv
import os
import pandas as pd
from algotrader.trading.ref_data import RefDataManager, Instrument, Currency, Exchange, RefDataManagerType


class MockRefDataManager(RefDataManager):
    """
    Usually it will be used as mock object in unit test
    TODO: should we move this class to tests folder?
    """
    def __init__(self, inst_df, ccy_df, exch_df ):
        self.inst_df = inst_df
        self.ccy_df = ccy_df
        self.exch_df = exch_df

        self.__inst_dict = {}
        self.__inst_symbol_dict = {}
        self.__ccy_dict = {}
        self.__exch_dict = {}

        self.start()

    def start(self):
        for index, row in self.inst_df.iterrows():
            inst = Instrument(inst_id=row['inst_id'], name=row['name'], type=row['type'], symbol=row['symbol'],
                              exch_id=row['exch_id'], ccy_id=row['ccy_id'], alt_symbol=row['alt_symbol'],
                              alt_exch_id=['alt_exch_id'], sector=row['sector'], group=row['group'],
                              put_call=row['put_call'], expiry_date=row['expiry_date'],
                              und_inst_id=row['und_inst_id'],
                              factor=row['factor'], strike=row['strike'], margin=row['margin'])
            self.add_inst(inst)

        for index, row in self.ccy_df.iterrows():
            ccy = Currency(ccy_id=row['ccy_id'], name=row['name'])
            self.add_ccy(ccy)

        for index, row in self.exch_df.iterrows():
            exch = Exchange(exch_id=row['exch_id'], name=row['name'])
            self.add_exch(exch)


    def stop(self):
        # No implememtation
        pass

    def add_inst(self, inst):
        if inst.inst_id in self.__inst_dict:
            raise RuntimeError("duplicate inst, inst_id=%s" % inst.inst_id)

        if inst.id() in self.__inst_symbol_dict:
            raise RuntimeError("duplicate inst, id=%s" % inst.id())

        self.__inst_dict[inst.inst_id] = inst
        self.__inst_symbol_dict[inst.id()] = inst

    def add_ccy(self, ccy):
        if ccy.ccy_id in self.__ccy_dict:
            raise RuntimeError("duplicate ccy, ccy_id %s" % ccy.ccy_id)

        self.__ccy_dict[ccy.ccy_id] = ccy

    def add_exch(self, exch):
        if exch.exch_id in self.__exch_dict:
            raise RuntimeError("duplicate exch, exch_id %s" % exch.exch_id)

        self.__exch_dict[exch.exch_id] = exch

    def get_insts(self, instruments):
        insts = []
        if isinstance(instruments, (list, tuple, set)):
            for instrument in instruments:
                if isinstance(instrument, (int, long)) or isinstance(instrument, str):
                    insts.append(self.search_inst(inst=instrument))
                elif isinstance(instrument, Instrument):
                    insts.append(instrument)
                else:
                    raise "Unknown instrument %s" % instrument
        elif isinstance(instruments, (int, long)) or isinstance(instruments, str):
            insts.append(self.search_inst(inst=instruments))
        elif isinstance(instruments, Instrument):
            insts.append(instruments)
        else:
            raise "Unknown instrument %s" % instruments

        return insts

    def get_inst(self, inst_id=None, symbol=None, exch_id=None):
        if isinstance(inst_id, int):
            return self.__inst_dict.get(inst_id, None)
        elif symbol and exch_id:
            return self.__inst_symbol_dict.get('%s@%s' % (symbol, exch_id), None)
        elif symbol:
            for key in self.__inst_dict:
                inst = self.__inst_dict[key]
                if inst.symbol == symbol:
                    return inst
        return None

    def search_inst(self, inst):
        if isinstance(inst, (int, long)):
            return self.__inst_dict.get(inst, None)
        elif inst in self.__inst_symbol_dict:
            return self.__inst_symbol_dict[inst]
        else:
            return self.get_inst(symbol=inst)

    def get_ccy(self, ccy_id):
        return self.__ccy_dict.get(ccy_id, None)

    def get_exch(self, exch_id):
        return self.__exch_dict.get(exch_id, None)

    def type(self):
        return RefDataManagerType.Mock



def build_inst_dataframe_from_list(symbols, type='ETF', exch_id='NYSE', ccy_id='USD'):
    inst_df = pd.DataFrame({'name': symbols})
    inst_df['type'] = type
    inst_df['symbol'] = inst_df['name']
    inst_df['exch_id'] = exch_id
    inst_df['ccy_id'] = ccy_id
    inst_df['alt_symbol'] = ''
    inst_df['alt_exch_id'] = ''
    inst_df['sector'] = ''
    inst_df['group'] = ''
    inst_df['put_call'] = ''
    inst_df['expiry_date'] = ''
    inst_df['und_inst_id'] = ''
    inst_df['factor'] = ''
    inst_df['strike'] = ''
    inst_df['margin'] = ''
    inst_df['inst_id'] = inst_df.index
    return inst_df



if __name__ == "__main__":

    symbols = ['SPY', 'VXX', 'XLV', 'XIV']
    inst_df = build_inst_dataframe_from_list(symbols)

#    ccy_id,name
    ccy_df = pd.DataFrame({ "ccy_id" : ["USD" , "HKD" ],
                            "name" : ["US Dollar", "HK Dollar"] })

    exchange_df = pd.DataFrame({"exch_id" : ["NYSE"],
                               "name" : ["New York Stock Exchange"]})

    mgr = MockRefDataManager(inst_df, ccy_df, exchange_df)
    print mgr.get_inst(symbol='VXX', exch_id='NYSE')
    print mgr.get_inst(inst_id=0)
    print mgr.get_inst(0)
