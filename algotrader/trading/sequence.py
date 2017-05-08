from algotrader import SimpleManager, Context
from algotrader.provider.datastore import PersistenceMode


class SequenceManager(SimpleManager):
    ID = "SequenceManager"

    def __init__(self):
        super(SequenceManager, self).__init__()
        self.store = None

    def _start(self, app_context: Context) -> None:
        self.store = self.app_context.get_data_store()
        self.persist_mode = self.app_context.config.get_app_config("persistenceMode")
        self.load_all()

    def load_all(self):
        if self.store:
            self.store.start(self.app_context)
            items = self.store.load_all('sequences')
            self.item_dict.update(items)

    def save_all(self):
        if self.store and self.persist_mode != PersistenceMode.Disable:
            for key, value in self.item_dict.items():
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

        if self.store and self.persist_mode == PersistenceMode.RealTime:
            self.store.save_sequence(id, initial)

    def all_items(self):
        return self.item_dict

    def has_item(self, id):
        return id in self.item_dict

    def id(self):
        return self.ID
