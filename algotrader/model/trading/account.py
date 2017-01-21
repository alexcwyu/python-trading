from algotrader.model.trade_data_pb2 import *
from algotrader.model.model_helper import ModelHelper
from algotrader.model.model_factory import ModelFactory

from typing import Dict, List, Callable, Union

class Account(object):
    def __init__(self, acct_id: str, values : Dict[str, AccountValue] = None, positions : Dict[str, Position] = None):
        # TODO load from DB
        self.account_state = ModelFactory.build_account_state(acct_id=acct_id, values=values, positions=positions)


    def on_acc_upd(self, account_update: AccountUpdate):
        self.account_state.values
        ModelHelper.add_to_dict_value(self.account_state.values, account_update.values)