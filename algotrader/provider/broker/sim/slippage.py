import abc

from algotrader.utils.trade_data import is_buy, is_sell


class Slippage(object):
    __metaclass__ = abc.ABCMeta

    def calc_price_w_bar(self, new_ord_req, price, qty, bar):
        return self.calc_price(new_ord_req, price, qty, bar.vol)

    def calc_price_w_quote(self, new_ord_req, price, qty, quote):
        if is_buy(new_ord_req):
            return self.calc_price(new_ord_req, price, qty, quote.bid_size)
        else:
            return self.calc_price(new_ord_req, price, qty, quote.ask_size)

    def calc_price_w_trade(self, new_ord_req, price, qty, trade):
        return self.calc_price(new_ord_req, price, qty, trade.size)

    @abc.abstractmethod
    def calc_price(self, new_ord_req, price, qty, avail_qty):
        raise NotImplementedError()


class NoSlippage(Slippage):
    def calc_price(self, new_ord_req, price, qty, avail_qty):
        return price


class VolumeShareSlippage(Slippage):
    def __init__(self, price_impact=0.1):
        self.price_impact = price_impact

    def calc_price(self, new_ord_req, price, qty, avail_qty):

        vol_share = float(qty) / float(avail_qty)
        impacted_price = vol_share ** 2 * self.price_impact
        if is_buy(new_ord_req):
            return price * (1 + impacted_price)
        else:
            return price * (1 - impacted_price)
