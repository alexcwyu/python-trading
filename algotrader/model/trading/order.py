from algotrader.model.trade_data_pb2 import *
from algotrader.model.model_helper import ModelHelper

class Order(object):
    def __init__(self, new_order_request: NewOrderRequest):
        self.order_state = order_state
        self.events = []

    def on_new_ord_req(self, nos):
        pass



    def on_ord_replace_req(self, ord_replace_req):
        self.events.append(ord_replace_req)

    def on_ord_cancel_req(self, ord_cancel_req):
        self.events.append(ord_cancel_req)