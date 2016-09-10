from algotrader import SimpleManager
from algotrader.trading.account import Account

class AccountManager(SimpleManager):
    def __init__(self):
        super(AccountManager, self).__init__()

    def _start(self, app_context, **kwargs):
        self.store = self.app_context.get_trade_data_store()
        self.load_all()

    def load_all(self):
        if self.store:
            accounts = self.store.load_all('accounts')
            for account in accounts:
                self.add(account)

    def save_all(self):
        if self.store:
            for account in self.all_items():
                self.store.save_account(account)

    def id(self):
        return "AccountManager"

    def new_account(self, name, values ={}):
        account = Account(name, values=values)
        self.add(account)
        return account