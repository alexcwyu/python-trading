import abc

from algotrader.utils.time_series import TimeSeries


class Indicator(TimeSeries):
    __metaclass__ = abc.ABCMeta

    _slots__ = (
        'input',
        'calculate',
    )

    def __init__(self, input, id, description):
        super(Indicator, self).__init__(id, description)
        self.input = input
        self.calculate = True
        self.input.subject.subscribe(self.on_time_value)
        self.update_all()

    def update_all(self):
        for time, value in self.input.get_data().items():
            self.on_time_value(time, value)

    def on_time_value(self, time_value):
        raise NotImplementedError()
