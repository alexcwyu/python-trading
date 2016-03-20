import abc

from algotrader.event.order import OrdAction


class SlippageModel(object):
    __metaclass__ = abc.ABCMeta

    def calc_price_w_bar(self, order, price, qty, used_qty, bar):
        return self.calc_price(order, price, qty, used_qty, bar.vol)

    def calc_price_w_quote(self, order, price, qty, used_qty, quote):
        if order.action == OrdAction.BUY:
            return self.calc_price(order, price, qty, used_qty, quote.bid_size)
        else:
            return self.calc_price(order, price, qty, used_qty, quote.ask_size)

    def calc_price_w_trade(self, order, price, qty, used_qty, trade):
        return self.calc_price(order, price, qty, used_qty, trade.size)

    @abc.abstractmethod
    def calc_price(self, order, price, qty, used_qty, total_avail_qty):
        raise NotImplementedError()


class NoSlippage(SlippageModel):
    def calc_price(self, order, price, qty, used_qty, total_avail_qty):
        return price


class VolumeShareSlippage(SlippageModel):

    def __init__(self, price_impact = 0.1):
        self.price_impact = price_impact

    def calc_price(self, order, price, qty, used_qty, total_avail_qty):

        total_qty = qty + used_qty
        vol_share = float(total_qty) / float(total_avail_qty)
        impacted_price = vol_share **2 * self.price_impact
        if order.is_buy():
            return price * (1 + impacted_price)
        else:
            return price * (1 - impacted_price)



