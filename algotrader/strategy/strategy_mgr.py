from importlib import import_module

from algotrader import SimpleManager


class StrategyManager(SimpleManager):
    def __init__(self):
        super(StrategyManager, self).__init__()
        self.stg_cls_dict = {}

    def _start(self, app_context, **kwargs):
        self.store = self.app_context.get_trade_data_store()
        self.load_all()

    def load_all(self):
        if self.store:
            self.store.start(self.app_context)
            strategies = self.store.load_all('strategies')
            for stg in strategies:
                self.add(stg)

    def save_all(self):
        if self.store:
            for stg in self.all_items():
                self.store.save_strategy(stg)

    def add(self, stg):
        super(StrategyManager, self).add(stg)
        if self.store:
            self.store.save_strategy(stg)

    def id(self):
        return "StrategyManager"

    def new_stg(self, trading_config):
        stg_id = trading_config.stg_id
        if self.has_item(stg_id):
            raise "Strategy Id %s already exist" % stg_id

        stg_cls = trading_config.stg_cls

        if stg_cls not in self.stg_cls_dict:
            module_name, cls_name = stg_cls.rsplit('.', 1)
            mod = import_module(module_name)
            cls = getattr(mod, cls_name)
            self.stg_cls_dict[stg_cls] = cls

        cls = self.stg_cls_dict[stg_cls]
        strategy = cls(stg_id=stg_id, trading_config=trading_config)
        self.add(strategy)
        return strategy


    def get_or_new_stg(self, trading_config):
        if self.has_item(trading_config.stg_id):
            return self.get(trading_config.stg_id)
        return self.new_stg(trading_config)