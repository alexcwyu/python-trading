import abc


class HasId(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()


class Startable(HasId):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.started = False

    def start(self, app_context=None, **kwargs):
        if not hasattr(self, "started") or not self.started:
            self.app_context=app_context
            self._start(app_context=app_context, **kwargs)
            self.started = True

    def stop(self):
        if self.started:
            self._stop()
            self.started = False

    def reset(self):
        pass

    @abc.abstractmethod
    def _start(self, app_context, **kwargs):
        raise NotImplementedError()

    def _stop(self):
        pass


class Manager(Startable):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Manager, self).__init__()


class SimpleManager(Manager):
    __metaclass__ = abc.ABCMeta

    __slots__ = (
        'item_dict'
    )

    def __init__(self):
        super(SimpleManager, self).__init__()
        self.item_dict = {}

    def get(self, id):
        return self.item_dict.get(id, None)

    def add(self, item):
        self.item_dict[item.id()] = item

    def all_items(self):
        return [item for item in self.item_dict.values()]

    def has_item(self, id):
        return id in self.item_dict

    def _load_all(self):
        pass

    def _save_all(self):
        pass

    def _start(self, app_context, **kwargs):
        self._load_all()

    def _stop(self):
        self._save_all()

        for item in self.item_dict.values():
            if isinstance(item, Startable):
                item.stop()

        self.reset()

    def reset(self):
        self.item_dict.clear()
