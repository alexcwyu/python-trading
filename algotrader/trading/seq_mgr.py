from algotrader import SimpleManager


class SequenceManager(SimpleManager):
    def __init__(self):
        super(SequenceManager, self).__init__()

    def _start(self, app_context, **kwargs):
        self.app_context = app_context
        self.store = self.app_context.get_seq_data_store()
        self.load_all()

    def load_all(self):
        if self.store:
            items = self.store.load_all('sequences')
            for item in items:
                self.add(item['_id'], item['seq'])

    def save_all(self):
        if self.store:
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

    def all_items(self):
        return self.item_dict

    def has_item(self, id):
        return id in self.item_dict

    def id(self):
        return "SequenceManager"
