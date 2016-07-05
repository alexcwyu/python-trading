class PortfolioManager:
    def __init__(self):
        self.__portf_dict = {}

    def add_portfolio(self, portfolio):
        self.__portf_dict[portfolio.portf_id] = portfolio

    def get_portfolio(self, portf_id):
        return self.__portf_dict[portf_id]


portf_mgr = PortfolioManager()
