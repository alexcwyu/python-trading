from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
import numpy as np


class Rank(PipeLine):
    _slots__ = (
    )

    def __init__(self, inputs, input_key='close', desc="Rank"):
        super(Rank, self).__init__(PipeLine.get_name(Rank.__name__, input),
                                   input, input_key, desc)
        super(Rank, self).update_all()

    def on_update(self, data):
        result = {}
        if self.all_filled():
            result[PipeLine.VALUE] = self.df.rank(axis=1, pct=True)
        else:
            # TODO: Shall we make the output as the same dimension as proper one?
            result[PipeLine.VALUE] = np.nan

        self.add(result)

