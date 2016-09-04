from algotrader import SimpleManager


class AccountManager(SimpleManager):
    def __init__(self, app_context=None):
        super(AccountManager, self).__init__()
        self.store = app_context

    def _load_all(self):
        if self.store:
            accounts = self.store.load_all('accounts')
            for account in accounts:
                self.add(account)

    def _save_all(self):
        if self.store:
            for account in self.all_items():
                self.store.save_account(account)


acct_mgr = AccountManager()
