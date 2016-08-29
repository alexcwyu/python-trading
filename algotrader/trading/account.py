from algotrader.event.event_handler import AccountEventHandler

from algotrader.provider.persistence.persist import Persistable
from algotrader.trading.position import PositionHolder


class Account(AccountEventHandler, PositionHolder, Persistable):
    __slots__ = (
        'name',
        'values',
        # 'positions',
        # 'open_orders'
    )

    def __init__(self, name=None):
        super(Account, self).__init__()
        self.name = name
        self.values = {}
        # self.positions = {}
        # self.open_orders = []

    def on_acc_upd(self, acc_upd):
        if acc_upd.key not in self.values:
            self.values[acc_upd.key] = {}
        self.values[acc_upd.key][acc_upd.ccy] = acc_upd.val

    def on_portf_upd(self, portf_upd):
        pass


    def id(self):
        return self.name
