import zerorpc

from algotrader.trading.order import OrderManager
from algotrader.utils.logging import logger


class RemoteOrderManager(OrderManager):
    def __init__(self, address="tcp://0.0.0.0:14242"):
        super(RemoteOrderManager, self).__init__()
        self.__address = address

    def _start(self, app_context):
        self.__server = zerorpc.Server(self)
        self.__server.bind(self.__address)
        logger.info("starting OMS")
        self.__server.run()

    def on_new_ord_req(self, order):
        logger.info("[%s] %s" % (self.__class__.__name__, order))
        return order

    def id(self):
        return "RemoteOrderManager"
