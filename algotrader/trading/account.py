from typing import Dict

from algotrader import SimpleManager
from algotrader.model.model_factory import ModelFactory
from algotrader.model.trade_data_pb2 import *
from algotrader.provider.datastore import PersistenceMode


class Account(object):
    def __init__(self, acct_id: str, values: Dict[str, AccountValue] = None, positions: Dict[str, Position] = None):
        # TODO load from DB
        self.__state = ModelFactory.build_account_state(acct_id=acct_id, values=values, positions=positions)

    def on_acc_upd(self, account_update: AccountUpdate) -> None:
        for update_value in account_update.values.values():
            ModelFactory.update_account_value(self.__state.values[update_value.key], update_value.key,
                                              update_value.ccy_values)

    def id(self) -> str:
        return self.__state.acct_id


class AccountManager(SimpleManager):
    def __init__(self):
        super(AccountManager, self).__init__()

    def _start(self, app_context):
        self.store = self.app_context.get_data_store()
        self.persist_mode = self.app_context.app_config.get_app_config("persistenceMode")
        self.load_all()

    def load_all(self):
        if hasattr(self, "store") and self.store:
            self.store.start(self.app_context)
            accounts = self.store.load_all('accounts')
            for account in accounts:
                self.add(account)

    def save_all(self):
        if hasattr(self, "store") and self.store and self.persist_mode != PersistenceMode.Disable:
            for account in self.all_items():
                self.store.save_account(account)

    def add(self, account):
        super(AccountManager, self).add(account)
        if hasattr(self, "store") and self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_account(account)

    def id(self):
        return "AccountManager"

    def new_account(self, name, values=None):
        if not values:
            values = {}
        account = Account(name, values=values)
        self.add(account)
        return account
