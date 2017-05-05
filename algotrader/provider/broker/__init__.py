import abc

from algotrader.event.event_handler import OrderEventHandler
from algotrader.provider import Provider


class Broker(Provider, OrderEventHandler):
    Simulator = "Simulator"
    IB = "IB"

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Provider, self).__init__()

    def _get_broker_config(self, path: str, default=None):
        return self.app_context.app_config.get_broker_config(self.id(), path, default=default)
