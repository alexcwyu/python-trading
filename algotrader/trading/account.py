from typing import Dict

from algotrader.model.model_factory import ModelFactory
from algotrader.model.model_helper import ModelHelper
from algotrader.model.trade_data_pb2 import *


class Account(object):
    def __init__(self, acct_id: str, values: Dict[str, AccountValue] = None, positions: Dict[str, Position] = None):
        # TODO load from DB
        self.account_state = ModelFactory.build_account_state(acct_id=acct_id, values=values, positions=positions)

    def on_acc_upd(self, account_update: AccountUpdate):

        for update_value in account_update.values.values():
            ModelFactory.update_account_value(self.account_state.values[update_value.key], update_value.key, update_value.ccy_values)
