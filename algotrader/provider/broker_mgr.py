from algotrader.tools import *

class BrokerManager():
    def __init__(self):
        self.__broker_mapping = {}

    def get_broker(self, broker_id):
        return self.__broker_mapping[broker_id]

    def reg_broker(self, broker):
        self.__broker_mapping[broker.id] = broker


broker_mgr = BrokerManager()