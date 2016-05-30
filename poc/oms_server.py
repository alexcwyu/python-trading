import zerorpc

from poc.zerorpc_patch import *
from algotrader.trading.order_mgr import OrderManager
from algotrader.utils import logger


class RemoteOrderManager(OrderManager):

    def __init__(self, address = "tcp://0.0.0.0:14242"):
        super(RemoteOrderManager, self).__init__()
        self.__address = address

    def start(self):
        self.__server = zerorpc.Server(self)
        self.__server.bind(self.__address)
        logger.info("starting OMS")
        self.__server.run()

    def on_order(self, order):
        logger.info("[%s] %s" % (self.__class__.__name__, order))
        return order


oms = RemoteOrderManager()
oms.start()