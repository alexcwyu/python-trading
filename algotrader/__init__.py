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

    @abc.abstractmethod
    def _start(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _stop(self):
        raise NotImplementedError()


class Managable(Startable):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.item_dict = {}

    def get(self, id):
        return self.item_dict.get(id, None)

    def add(self, item):
        self.item_dict[item.id()] = item
