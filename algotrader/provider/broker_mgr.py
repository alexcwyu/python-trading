from algotrader.tools import *

class BrokerManager():
    def __init__(self):
        self.__broker_mapping = {}

    def get_broker(self, broker_id):
        if broker_id in self.__broker_mapping:
            return self.__broker_mapping[broker_id]
        return None

    def reg_broker(self, broker):
        self.__broker_mapping[broker.id()] = broker


broker_mgr = BrokerManager()