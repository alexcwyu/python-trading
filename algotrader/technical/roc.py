import datetime

import numpy as np

from algotrader.technical import Indicator
from algotrader.utils.time_series import TimeSeries


class ROC(Indicator):
    _slots__ = (
        'ago'
    )

    def __init__(self, input, ago=1, description="Rate Of Change"):
        super(ROC, self).__init__(input, "ROC(%s, %s)" % (input.id, ago), description)
        self.ago = ago

    def on_update(self, time_value):
        time, value = time_value
        if self.input.size() > self.ago:
            prev_value = self.input.ago(self.ago)
            curr_value = self.input.now()
            if prev_value != 0.0:
                value = (curr_value - prev_value) / prev_value
                self.add(time, value)
            else:
                self.add(time, np.nan)
        else:
            self.add(time, np.nan)



