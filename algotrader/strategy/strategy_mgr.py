class StrategyManager:
    def __init__(self):
        self.__stg_dict = {}

    def add_strategy(self, strategy):
        self.__stg_dict[strategy.stg_id] = strategy

    def get_strategy(self, stg_id):
        return self.__stg_dict.get(stg_id, None)


stg_mgr = StrategyManager()
