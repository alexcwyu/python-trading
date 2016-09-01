class StrategyManager:
    def __init__(self, store=None):
        self.__stg_dict = {}
        self.store = store

    def add_strategy(self, strategy):
        self.__stg_dict[strategy.stg_id] = strategy

    def get_strategy(self, stg_id):
        return self.__stg_dict.get(stg_id, None)

    def clear(self):
        for stg in self.__stg_dict.itervalues():
            stg.stop()
        self.__stg_dict.clear()

    def start(self):
        if not self.started:
            self.started = True
            self.load()

    def stop(self):
        if self.started:
            self.save()
            self.clear()
            self.started = False

    def load(self):
        if self.store:
            self.__stg_dict = {}
            strategies = self.store.load_all('strategies')
            for stg in strategies:
                self.add_strategy(stg)

    def save(self):
        if self.store:
            for stg in self.all_strategies():
                self.store.save_strategy(stg)

    def all_strategies(self):
        return [stg for stg in self.__stg_dict.values()]


stg_mgr = StrategyManager()
