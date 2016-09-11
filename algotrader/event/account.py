from algotrader.event.event import Event


class AccountEvent(Event):
    def __init__(self, timestamp=None):
        super(AccountEvent, self).__init__(timestamp)


class AccountUpdate(AccountEvent):
    __slots__ = (
        'account_name',
        'key',
        'ccy',
        'val',
    )

    def __init__(self, id =None ,account_name=None, key=None, ccy=None, val=0.0, timestamp=None):
        super(AccountUpdate, self).__init__(timestamp=timestamp)
        self.id = id
        self.account_name = account_name
        self.key = key
        self.ccy = ccy
        self.val = val

    def on(self, handler):
        handler.on_acc_upd(self)

    def id(self):
        return self.id


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

    def __init__(self, id =None, inst_id=None, position=0, mkt_price=0, mkt_value=0, avg_cost=0, unrealized_pnl=0, realized_pnl=0,
                 account_name=None, timestamp=None):
        super(PortfolioUpdate, self).__init__(timestamp=timestamp)
        self.id = id
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

    def id(self):
        return self.id
