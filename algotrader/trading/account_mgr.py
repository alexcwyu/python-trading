from algotrader import SimpleManager


class AccountManager(SimpleManager):
    def __init__(self):
        super(AccountManager, self).__init__()

    def _start(self, app_context, **kwargs):
        self.store = self.app_context.get_trade_data_store()
        self._load_all()

    def _load_all(self):
        if self.store:
            accounts = self.store.load_all('accounts')
            for account in accounts:
                self.add(account)

    def _save_all(self):
        if self.store:
            for account in self.all_items():
                self.store.save_account(account)

    def id(self):
        return "AccountManager"
