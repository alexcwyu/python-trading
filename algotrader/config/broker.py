import abc

from algotrader.config.config import Config
from algotrader.provider.broker.sim.commission import Commission
from algotrader.provider.broker.sim.fill_strategy import FillStrategy


class BrokerConfig(Config):
    IBConfig = "IBConfig"
    SimulatorConfig = "SimulatorConfig"

    __metaclass__ = abc.ABCMeta


class IBConfig(BrokerConfig):
    __slots__ = (
        'host',
        'port',
        'client_id',
        'account',
        'daemon',
        'next_request_id',
        'next_order_id',
    )

    def __init__(self, host='localhost',
                 port=4001,
                 client_id=0,
                 account = None,
                 daemon=False,
                 next_request_id =1,
                 next_order_id = None):
        super(IBConfig, self).__init__(BrokerConfig.IBConfig)
        self.host = host
        self.port = port
        self.client_id = client_id
        self.account = account
        self.daemon = daemon
        self.next_request_id = next_request_id
        self.next_order_id = next_order_id


class SimulatorConfig(BrokerConfig):
    __slots__ = (
        'commission_id',
        'fill_strategy_id',
        'next_ord_id',
        'next_exec_id'
    )

    def __init__(self, commission_id=Commission.Default, fill_strategy_id=FillStrategy.Default, next_ord_id=0, next_exec_id=0):
        super(SimulatorConfig, self).__init__(BrokerConfig.SimulatorConfig)
        self.commission_id = commission_id
        self.fill_strategy_id = fill_strategy_id
        self.next_ord_id = next_ord_id
        self.next_exec_id = next_exec_id
