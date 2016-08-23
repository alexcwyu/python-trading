from algotrader.event.event_handler import AccountEventHandler

from collections import defaultdict

class Account(AccountEventHandler):
    def __init__(self, name):
        self.name = name
        self.key_ccy_value = defaultdict(dict)
        self.positions = {}
        self.open_orders = []

    def on_acc_upd(self, acc_upd):
        self.key_ccy_value[acc_upd.key][acc_upd.ccy] = acc_upd.val

    def on_portf_upd(self, portf_upd):
        pass

    def on_order(self, order):
        pass