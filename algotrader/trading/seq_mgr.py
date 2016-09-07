from algotrader import SimpleManager


class SequenceManager(SimpleManager):
    Order = 'order'

    def __init__(self, app_context=None):
        super(SimpleManager, self).__init__()
        self.app_context = app_context

    def _start(self):
        self.store = self.app_context.get_seq_data_store()
        self._load_all()

    def _load_all(self):
        if self.store:
            sequences = self.store.load_all('sequences')
            for sequence in sequences:
                self.add(sequence)

    def _save_all(self):
        if self.store:
            for sequence in self.all_items():
                self.store.save_sequence(sequence)

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

    def all_items(self):
        return [item for item in self.item_dict.values()]

    def has_item(self, id):
        return id in self.item_dict
