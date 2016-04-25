'''
Created on 4/15/16
@author = 'jason'
'''

import os
import pandas as pd
from swigibpy import (EWrapper, EPosixClientSocket, Contract, Order, TagValue,
                      TagValueList)

class InstrumentManager(object):
    def __init__(self):
        self.fileloc = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instrument.csv'))
        self.start()

    def start(self):
        self.instrument_repo = pd.read_csv(self.fileloc)
        self.instrument_repo = self.instrument_repo.set_index('id')

    def stop(self):
        self.instrument_repo.to_csv(self.fileloc)



class IBContractFactory(object):
    def __init__(self, instru_mgr=None):
        if not instru_mgr :
            instru_mgr = InstrumentManager()
            instru_mgr.start()
        self.instru_mgr = instru_mgr


    def buildStockOrCashContract(self, symbol):
        df = self.instru_mgr.instrument_repo
        instru_row = df[df["symbol"] == symbol]

        contract = Contract()
        contract.symbol = instru_row["altSymbol"].values[0] # like OQ use altSymbol that is used by IB
        contract.secType = instru_row["secType"].values[0]
        contract.exchange = instru_row["exchange"].values[0]
        contract.currency = instru_row["currency"].values[0]

        expiry = instru_row["expiry"].values[0]
        if not expiry or expiry != '':
            contract.expiry = instru_row["expiry"].values[0]

        multi = instru_row["multiplier"].values[0]
        if not multi or multi != '':
            contract.multiplier = instru_row["multiplier"].values[0]

        strike = instru_row["strike"].values[0]
        if not strike or strike != '':
            contract.strike = instru_row["strike"].values[0]

        return contract



#instru_mgr = InstrumentManager()