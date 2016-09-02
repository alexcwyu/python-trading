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
