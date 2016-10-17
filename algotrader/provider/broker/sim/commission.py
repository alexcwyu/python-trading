import abc


class Commission(object):
    Default = 0

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def calc(self, new_ord_req, price, qty):
        raise NotImplementedError()


class NoCommission(Commission):
    def calc(self, new_ord_req, price, qty):
        return 0


class FixedPerTrade(Commission):
    def __init__(self, amount):
        self.amount = amount

    def calc(self, new_ord_req, price, qty):
        return self.amount


class TradePercentage(Commission):
    def __init__(self, percentage):
        self.percentage = percentage

    def calc(self, new_ord_req, price, qty):
        return price * qty * self.percentage
