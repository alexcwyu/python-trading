import abc


from algotrader.provider.provider import broker_mgr, Broker
from algotrader.provider.broker.order_handler import MarketOrderHandler, LimitOrderHandler, StopLimitOrderHandler, \
    StopOrderHandler, TrailingStopOrderHandler
from algotrader.provider.broker.sim_config import SimConfig

class FillStrategy(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process_new_order(self, order):
        raise NotImplementedError()

    @abc.abstractmethod
    def process_market_data(self, market_data):
        raise NotImplementedError()

    def set_sim_config(self, sim_config):
        self.sim_config = sim_config


class DefaultFillStrategy(FillStrategy):

    def __init__(self):
        self.__market_ord_handler = MarketOrderHandler(self.execute, self.__sim_config)
        self.__limit_ord_handler = LimitOrderHandler(self.execute, self.__sim_config)
        self.__stop_limit_ord_handler = StopLimitOrderHandler(self.execute, self.__sim_config)
        self.__stop_ord_handler = StopOrderHandler(self.execute, self.__sim_config)
        self.__trailing_stop_ord_handler = TrailingStopOrderHandler(self.execute, self.__sim_config)

    def process_new_order(self, order):
        pass

    def process(self, order, market_data):
        pass