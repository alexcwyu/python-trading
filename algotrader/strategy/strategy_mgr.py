from algotrader import SimpleManager


class StrategyManager(SimpleManager):
    def __init__(self):
        super(StrategyManager, self).__init__()

    def _start(self, app_context, **kwargs):
        self.store = self.app_context.get_trade_data_store()
        self._load_all()

    def _load_all(self):
        if self.store:
            strategies = self.store.load_all('strategies')
            for stg in strategies:
                self.add(stg)

    def _save_all(self):
        if self.store:
            for stg in self.all_items():
                self.store.save_strategy(stg)

    def id(self):
        return "StrategyManager"
