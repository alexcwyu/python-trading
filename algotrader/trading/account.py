from typing import Dict

from algotrader import SimpleManager, Context, Startable, HasId
from algotrader.model.model_factory import ModelFactory
from algotrader.model.trade_data_pb2 import *
from algotrader.provider.datastore import PersistenceMode

from algotrader.model.trade_data_pb2 import *

class Account(Startable, HasId):
    def __init__(self, acct_id: str, values: Dict[str, AccountValue] = None, state=None):
        # TODO load from DB
        self.state = state if state else ModelFactory.build_account_state(acct_id=acct_id, values=values)

    def on_acc_upd(self, account_update: AccountUpdate) -> None:
        for update_value in account_update.values.values():
            ModelFactory.update_account_value(self.state.values[update_value.key], update_value.key,
                                              update_value.ccy_values)

    def id(self) -> str:
        return self.state.acct_id

    def _start(self, app_context: Context) -> None:
        # TODO
        pass


class AccountManager(SimpleManager):
    def __init__(self):
        super(AccountManager, self).__init__()
        self.store = None

    def _start(self, app_context: Context) -> None:
        self.store = self.app_context.get_data_store()
        self.persist_mode = self.app_context.config.get_app_config("persistenceMode")
        self.load_all()

    def load_all(self):
        if self.store:
            self.store.start(self.app_context)
            account_states = self.store.load_all(AccountState)
            for account_state in account_states:
                self.add(self.new_account(account_state.acct_id, state=account_state))

    def save_all(self):
        if self.store and self.persist_mode != PersistenceMode.Disable:
            for account in self.all_items():
                self.store.save_account(account)

    def add(self, account):
        super(AccountManager, self).add(account)
        if self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_account(account)

    def id(self):
        return "AccountManager"

    def new_account(self, acct_id, values=None, state=None):
        account = Account(acct_id, values=values, state=state)
        self.add(account)
        return account
