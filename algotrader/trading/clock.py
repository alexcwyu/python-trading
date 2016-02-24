import abc


class Clock(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def current_date_time(self):
        pass


class RealTimeClock(Clock):
    pass


class SimulationClock(Clock):
    pass
