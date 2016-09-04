import abc

from algotrader.config.config import Config


class BrokerConfig(Config):
    __metaclass__ = abc.ABCMeta


class IBConfig(BrokerConfig):
    __slots__ = (
        'host',
        'port',
        'client_id'
    )

    def __init__(self, id='IB', host='localhost',
                 port=4001,
                 client_id=0):
        super(IBConfig, self).__init__(id)
        self.host = host
        self.port = port
        self.client_id = client_id
