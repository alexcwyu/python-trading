from algotrader.trading.instrument_data import inst_data_mgr
from algotrader.utils.time_series import TimeSeries


class Indicator(TimeSeries):
    _slots__ = (
        'input',
        'calculate',
    )

    def __init__(self, input, id, description):
        super(Indicator, self).__init__(id, description)

        if isinstance(input, TimeSeries):
            self.input = input
        else:
            self.input = inst_data_mgr.get_series(input)
        self.input.subject.subscribe(self.on_update)
        inst_data_mgr.add_series(self)
        self.calculate = True
        self.update_all()

    def update_all(self):
        for time, value in self.input.get_data().items():
            self.on_update(time, value)

    def on_update(self, time_value):
        raise NotImplementedError()
