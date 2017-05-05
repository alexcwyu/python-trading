import abc


class Analyzer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update(self, timestamp: int, total_equity: float):
        return
