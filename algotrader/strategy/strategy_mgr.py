from algotrader import SimpleManager


class StrategyManager(SimpleManager):
    def __init__(self, app_context=None):
        super(StrategyManager, self).__init__()
        self.app_context = app_context

    def _load_all(self):
        if self.store:
            strategies = self.store.load_all('strategies')
            for stg in strategies:
                self.add(stg)

    def _save_all(self):
        if self.store:
            for stg in self.all_items():
                self.store.save_strategy(stg)


stg_mgr = StrategyManager()
