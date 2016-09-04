import abc


class Startable(object):
    __metaclass__ = abc.ABCMeta

    __slots__ = (
        'started'
    )

    def __init__(self):
        self.started = False

    def start(self):
        if not self.started:
            self._start()
            self.started = True

    def stop(self):
        if self.started:
            self._stop()
            self.started = False

    def reset(self):
        pass

    @abc.abstractmethod
    def _start(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _stop(self):
        raise NotImplementedError()


class Manager(Startable):
    __metaclass__ = abc.ABCMeta

    __slots__ = (
        'item_dict'
    )

    def __init__(self):
        super(Manager, self).__init__()
        self.item_dict = {}

    @abc.abstractmethod
    def _load_all(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _save_all(self):
        raise NotImplementedError()

    def _start(self):
        self._load_all()

    def _stop(self):
        self._save_all()
        self.reset()

    def reset(self):
        self.item_dict.clear()


class SimpleManager(Manager):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(SimpleManager, self).__init__()

    def get(self, id):
        return self.item_dict.get(id, None)

    def add(self, item):
        self.item_dict[item.id()] = item

    def all_items(self):
        return [item for item in self.item_dict.values()]

    def has_item(self, id):
        return id in self.item_dict
