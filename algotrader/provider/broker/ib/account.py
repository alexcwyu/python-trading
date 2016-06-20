from algotrader.event.event import Event, EventHandler


class AccountEvent(Event):
    def __init__(self, timestamp=None):
        super(AccountEvent, self).__init__(timestamp)


class AccountUpdate(AccountEvent):
    __slots__ = (
        'account_name',
        'key',
        'val',
        'ccy',
    )

    def __init__(self, account_name, key, val, ccy, timestamp=None):
        super(AccountUpdate, self).__init__(timestamp=timestamp)
        self.account_name = account_name
        self.key = key
        self.val = val
        self.ccy = ccy

    def on(self, handler):
        handler.on_acc_upd(self)


class PortfolioUpdate(AccountEvent):
    __slots__ = (
        'inst_id',
        'position',
        'mkt_price',
        'mkt_value',
        'avg_cost',
        'unrealized_pnl',
        'realized_pnl',
        'account_name'
    )

    def __init__(self, inst_id, position, mkt_price, mkt_value, avg_cost, unrealized_pnl, realized_pnl,
                 account_name, timestamp=None):
        super(PortfolioUpdate, self).__init__(timestamp=timestamp)
        self.inst_id = inst_id
        self.position = position
        self.mkt_price = mkt_price
        self.mkt_value = mkt_value
        self.avg_cost = avg_cost
        self.unrealized_pnl = unrealized_pnl
        self.realized_pnl = realized_pnl
        self.account_name = account_name

    def on(self, handler):
        handler.on_portf_upd(self)


class AccountEventEventHandler(EventHandler):
    def on_acc_upd(self, acc_upd):
        pass

    def on_portf_upd(self, portf_upd):
        pass


class AccountValue:
    __slots__ = (
        'key',
        'value'
    )

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return '%s = %s' % (self.key, self.value)


class Account(AccountEventEventHandler):
    def __init__(self, name):
        self.name = name
        self.account_value = {}
        self.positions = {}
        self.open_orders = []

    def on_acc_upd(self, acc_upd):
        pass

    def on_portf_upd(self, portf_upd):
        pass

    def on_order(self, order):
        pass
