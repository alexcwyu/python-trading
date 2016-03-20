import abc


class Commission(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def calc(self, order, price, qty):
        raise NotImplementedError()


class NoCommission(Commission):
    def calc(self, order, price, qty):
        return 0


class FixedPerTrade(Commission):
    def __init__(self, amount):
        self.amount = amount

    def calc(self, order, price, qty):
        if len(order.exec_reports) > 0:
            return self.amount
        return 0


class TradePercentage(Commission):
    def __init__(self, percentage):
        self.percentage = percentage

    def calc(self, order, price, qty):
        return price * qty * self.percentage
