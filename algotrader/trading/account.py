from algotrader import Startable, HasId
from algotrader.event.event_handler import AccountEventHandler
from algotrader.provider.persistence import Persistable
from algotrader.trading.position import PositionHolder


class Account(AccountEventHandler, PositionHolder, Persistable, Startable):
    __slots__ = (
        'acct_id',
        'values',
        # 'positions',
        # 'open_orders'
    )

    __transient__ = (
        'app_context',
    )
    def __init__(self, acct_id=None, values=None):
        super(Account, self).__init__()
        self.acct_id = acct_id
        self.values = values if values else {}
        # self.positions = {}
        # self.open_orders = []

    def on_acc_upd(self, acc_upd):
        if acc_upd.key not in self.values:
            self.values[acc_upd.key] = {}
        self.values[acc_upd.key][acc_upd.ccy] = acc_upd.val

    def on_portf_upd(self, portf_upd):
        pass

    def id(self):
        return self.acct_id

    def _start(self, app_context, **kwargs):
        self.app_context.acct_mgr.add(self)

    def _stop(self):
        pass
