import numpy as np
from typing import Dict

from algotrader import Context
from algotrader.technical import DataSeries
from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
from algotrader.utils.data_series import get_input_name


class Pairwise(PipeLine):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise", func=None, length=1):
        super(Pairwise, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                       length=length)
        self.func = func

    def _start(self, app_context: Context) -> None:
        super(Pairwise, self)._start(self.app_context)
        input_lhs = self.get_input(0)
        input_rhs = self.get_input(1)
        self.lhs_name = get_input_name(input_lhs)
        self.rhs_name = get_input_name(input_rhs)

        if isinstance(input_lhs, PipeLine) and not isinstance(input_rhs, PipeLine):
            raise TypeError("input_lhs has to be the same type as input_rhs as Pipeline")

        if isinstance(input_lhs, Indicator) and not isinstance(input_rhs, Indicator):
            raise TypeError("input_lhs has to be the same type as input_rhs as Indicator")

        if isinstance(input_lhs, DataSeries) and not isinstance(input_rhs, DataSeries):
            raise TypeError("input_lhs has to be the same type as input_rhs as DataSeries")

        if isinstance(input_lhs, PipeLine):
            try:
                np.testing.assert_almost_equal(input_lhs.shape(), input_rhs.shape(), 10)
                self.__shape = input_lhs.shape()
            except AssertionError as e:
                raise ValueError("input_lhs shape should be the same as input_rhs in Pairwise Pipeline operation!")
        else:
            self.__shape = np.array([1, 1])

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        super(Pairwise, self)._process_update(source=source, timestamp=timestamp, data=data)
        result = {}
        if self.inputs[0].size() >= self.length:
            if self.all_filled():
                x = self.cache[self.lhs_name][-self.length:] if self.length > 1 else self.cache[self.lhs_name][-1]
                y = self.cache[self.rhs_name][-self.length:] if self.length > 1 else self.cache[self.rhs_name][-1]
                result[PipeLine.VALUE] = self.func(x, y)
            else:
                result[PipeLine.VALUE] = self._default_output()
        else:
            result[PipeLine.VALUE] = self._default_output()

        self.add(timestamp=timestamp, data=result)

    def _default_output(self):
        na_array = np.empty(shape=self.shape())
        na_array[:] = np.nan
        return na_array

    def shape(self):
        return self.__shape


class Plus(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise Plus"):
        super(Plus, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc, func=lambda x, y: x + y)


class Minus(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise Minus"):
        super(Minus, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc, func=lambda x, y: x - y)


class Times(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise Times"):
        super(Times, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc, func=lambda x, y: x * y)


class Divides(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise Divdes"):
        super(Divides, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc, func=lambda x, y: x / y)


class Greater(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise Greater"):
        super(Greater, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc, func=lambda x, y: x > y)


class GreaterOrEquals(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise GreaterOrEquals"):
        super(GreaterOrEquals, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc, func=lambda x, y: x >= y)


class Less(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise Less"):
        super(Less, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc, func=lambda x, y: x < y)


class LessOrEquals(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise LessOrEquals"):
        super(LessOrEquals, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc, func=lambda x, y: x <= y)


class Equals(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise Equals"):
        super(Equals, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc, func=lambda x, y: x == y)


class NotEquals(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise NotEquals"):
        super(NotEquals, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc, func=lambda x, y: x != y)


class Min(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise Min"):
        super(Min, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                   func=lambda x, y: np.min(np.vstack([x, y]), axis=0))


class Max(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise Max"):
        super(Max, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                   func=lambda x, y: np.max(np.vstack([x, y]), axis=0))


class PairCorrelation(Pairwise):
    def __init__(self, time_series=None, inputs=None, input_keys='close', desc="Pairwise PairCorrelation"):
        super(PairCorrelation, self).__init__(time_series=time_series, inputs=inputs, input_keys=input_keys, desc=desc,
                                   func=lambda x, y: np.corrcoef(x, y)[0, 1])

#
# from jinja2 import Template
# pairwiseTemplate = Template(
# """
# class {{className}}(Pairwise):
#     def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise {{className}}"):
#         super({{className}}, self).__init__(input_lhs, input_rhs, func={{func}},
#                                       name=PipeLine.get_name({{className}}.__name__, [input_lhs, input_rhs], input_key),
#                                       input_key=input_key, desc=desc)
# """
# )

# print pairwiseTemplate.render({"className" : "Min",
#                          "func" : "lambda x, y: np.min(np.vstack([x, y]), axis=0)"})
#
# print pairwiseTemplate.render({"className" : "Max",
#                                "func" : "lambda x, y: np.max(np.vstack([x, y]), axis=0)"})
#
# print pairwiseTemplate.render({"className": "PairCorrelation",
#                                 "func" : "lambda x, y: np.corrcoef(x, y)[0,1]"})
