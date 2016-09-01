import abc

from algotrader.config.config import Config


class BrokerConfig(Config):
    __metaclass__ = abc.ABCMeta


class IBConfig(BrokerConfig):
    __metaclass__ = abc.ABCMeta

    __slots__ = (
        'host',
        'port',
        'client_id'
    )

    def __init__(self, host,
                 port,
                 client_id):
        self.host = host

        self.port = port
        self.client_id = client_id
