from algotrader.provider import ProviderManager
from algotrader.provider.broker import Broker
from algotrader.provider.broker.sim.simulator import Simulator
from algotrader.provider.broker.ib.ib_broker import IBBroker

class BrokerManager(ProviderManager):
    def __init__(self, app_context):
        super(BrokerManager, self).__init__()
        self.app_context = app_context

        self.add(Simulator())
        self.add(IBBroker())

    def add(self, provider):
        if provider and isinstance(provider, Broker):
            super(BrokerManager, self).add(provider)

    def _start(self):
        self.app_config.broker_configs
        ## TODO foreach config: init broker with config


broker_mgr = BrokerManager()