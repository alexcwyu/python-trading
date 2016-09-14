from algotrader import SimpleManager
from algotrader.config.persistence import PersistenceMode


class SequenceManager(SimpleManager):
    def __init__(self):
        super(SequenceManager, self).__init__()

    def _start(self, app_context, **kwargs):
        self.app_context = app_context
        self.store = self.app_context.get_seq_data_store()
        self.persist_mode = self.app_context.app_config.persistence_config.seq_persist_mode
        self.load_all()

    def load_all(self):
        if hasattr(self, "store") and self.store:
            self.store.start(self.app_context)
            items = self.store.load_all('sequences')
            self.item_dict.update(items)

    def save_all(self):
        if hasattr(self, "store") and self.store and self.persist_mode != PersistenceMode.Disable:
            for key, value in self.item_dict.iteritems():
                self.store.save_sequence(key, value)

    def get(self, id):
        return self.item_dict.get(id, None)

    def get_next_sequence(self, id):
        if id not in self.item_dict:
            self.add(id)
        current = self.item_dict[id]
        self.item_dict[id] += 1
        return current

    def add(self, id, initial=1):
        self.item_dict[id] = initial

        if hasattr(self, "store") and self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_sequence(id, initial)

    def all_items(self):
        return self.item_dict

    def has_item(self, id):
        return id in self.item_dict

    def id(self):
        return "SequenceManager"
