class AccountManager:
    def __init__(self, store=None):
        self.__acct_dict = {}
        self.store = store

    def add_account(self, account):
        self.__acct_dict[account.name] = account

    def get_account(self, name):
        return self.__acct_dict.get(name, None)

    def clear(self):
        for acct in self.__acct_dict.itervalues():
            acct.stop()
        self.__acct_dict.clear()


    def start(self):
        if not self.started:
            self.started = True
            self.load()

    def stop(self):
        if self.started:
            self.save()
            self.clear()
            self.started = False

    def load(self):
        if self.store:
            self.__acct_dict = {}
            accounts = self.store.load_all('accounts')
            for account in accounts:
                self.add_account(account)

    def save(self):
        if self.store:
            for account in self.all_accounts():
                self.store.save_account(account)


    def all_accounts(self):
        return [port for port in self.__acct_dict.values()]

acct_mgr = AccountManager()
