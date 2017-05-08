import abc
from algotrader.utils.model import get_model_id

class HasId(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def id(self) -> str:
        raise NotImplementedError()



class Startable(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.started = False

    def start(self, app_context = None) -> None:
        self.app_context = app_context
        if not hasattr(self, "started") or not self.started:
            self.started = True
            self._start(app_context=app_context)

    def stop(self) -> None:
        if hasattr(self, "started") and self.started:
            self._stop()
            self.started = False

    def reset(self) -> None:
        pass

    def _start(self, app_context = None) -> None:
        pass

    def _stop(self) -> None:
        pass


class Context(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.startables = []

    def add_startable(self, startable: Startable) -> Startable:
        self.startables.append(startable)
        return startable

    def start(self) -> None:
        for startable in self.startables:
            startable.start(self)

    def stop(self) -> None:
        for startable in reversed(self.startables):
            startable.stop()

    @abc.abstractmethod
    def get_data_store(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_broker(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_feed(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_portfolio(self):
        raise NotImplementedError()


class Manager(Startable, HasId):
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
        self.item_dict[get_model_id(item)] = item

    def all_items(self):
        return [item for item in self.item_dict.values()]

    def has_item(self, id) -> bool:
        return id in self.item_dict

    def load_all(self):
        pass

    def save_all(self):
        pass

    def _start(self, app_context: Context) -> None:
        self.load_all()

    def _stop(self) -> None:
        self.save_all()

        for item in self.item_dict.values():
            if isinstance(item, Startable):
                item.stop()

        self.reset()

    def reset(self) -> None:
        self.item_dict.clear()
