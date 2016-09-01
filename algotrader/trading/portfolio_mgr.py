class PortfolioManager:
    def __init__(self, store=None):
        self.__portf_dict = {}
        self.store = store

    def add_portfolio(self, portfolio):
        self.__portf_dict[portfolio.portf_id] = portfolio

    def get_portfolio(self, portf_id):
        return self.__portf_dict.get(portf_id, None)

    def clear(self):
        for port in self.__portf_dict.itervalues():
            port.stop()
        self.__portf_dict.clear()


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
            self.__portf_dict = {}
            portfolios = self.store.load_all('portfolios')
            for portfolio in portfolios:
                self.add_portfolio(portfolio)

    def save(self):
        if self.store:
            for portfolio in self.all_portfolios():
                self.store.save_portfolio(portfolio)


    def all_portfolios(self):
        return [port for port in self.__portf_dict.values()]

portf_mgr = PortfolioManager()
