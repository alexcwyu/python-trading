from algotrader.model.trade_data_pb2 import *


class TradeDataUtils(object):
    @staticmethod
    def is_buy(new_order_req: NewOrderRequest):
        return new_order_req.action == Buy

    @staticmethod
    def is_sell(new_order_req: NewOrderRequest):
        return new_order_req.action == Sell
