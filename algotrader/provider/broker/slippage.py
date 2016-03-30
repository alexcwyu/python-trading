import abc

from algotrader.event.order import OrdAction


class Slippage(object):
    __metaclass__ = abc.ABCMeta

    def calc_price_w_bar(self, order, price, qty, bar):
        return self.calc_price(order, price, qty, bar.vol)

    def calc_price_w_quote(self, order, price, qty, quote):
        if order.is_buy():
            return self.calc_price(order, price, qty, quote.bid_size)
        else:
            return self.calc_price(order, price, qty, quote.ask_size)

    def calc_price_w_trade(self, order, price, qty, trade):
        return self.calc_price(order, price, qty, trade.size)

    @abc.abstractmethod
    def calc_price(self, order, price, qty, avail_qty):
        raise NotImplementedError()


class NoSlippage(Slippage):
    def calc_price(self, order, price, qty, avail_qty):
        return price


class VolumeShareSlippage(Slippage):

    def __init__(self, price_impact = 0.1):
        self.price_impact = price_impact

    def calc_price(self, order, price, qty, avail_qty):

        vol_share = float(qty) / float(avail_qty)
        impacted_price = vol_share **2 * self.price_impact
        if order.is_buy():
            return price * (1 + impacted_price)
        else:
            return price * (1 - impacted_price)



