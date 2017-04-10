from algotrader import SimpleManager
from importlib import import_module

from algotrader.config.persistence import PersistenceMode


class StrategyManager(SimpleManager):
    def __init__(self):
        super(StrategyManager, self).__init__()
        self.stg_cls_dict = {}

    def _start(self, app_context, **kwargs):
        self.store = self.app_context.get_trade_data_store()
        self.persist_mode = self.app_context.app_config.persistence_config.trade_persist_mode
        self.load_all()

    def load_all(self):
        if hasattr(self, "store") and self.store:
            self.store.start(self.app_context)
            strategies = self.store.load_all('strategies')
            for stg in strategies:
                self.add(stg)

    def save_all(self):
        if hasattr(self, "store") and self.store and self.persist_mode != PersistenceMode.Disable:
            for stg in self.all_items():
                self.store.save_strategy(stg)

    def add(self, stg):
        super(StrategyManager, self).add(stg)
        if hasattr(self, "store") and self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_strategy(stg)

    def id(self):
        return "StrategyManager"

    def new_stg(self, stg_id, stg_cls, stg_configs=None):
        if self.has_item(stg_id):
            raise "Strategy Id %s already exist" % stg_id

        if stg_cls not in self.stg_cls_dict:
            module_name, cls_name = stg_cls.rsplit('.', 1)
            mod = import_module(module_name)
            cls = getattr(mod, cls_name)
            self.stg_cls_dict[stg_cls] = cls

        cls = self.stg_cls_dict[stg_cls]
        strategy = cls(stg_id=stg_id, stg_configs=stg_configs)
        self.add(strategy)
        return strategy

    def get_or_new_stg(self, app_config):
        stg_id = app_config.stg_id
        stg_cls = app_config.stg_cls
        stg_configs = app_config.stg_configs
        if self.has_item(stg_id):
            stg = self.get(stg_id)
            stg.stg_configs = stg_configs
            return stg
        return self.new_stg(stg_id, stg_cls, stg_configs)
