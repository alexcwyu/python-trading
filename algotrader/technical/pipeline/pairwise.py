import numpy as np

from algotrader.technical import DataSeries
from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
from algotrader.trading.data_series import DataSeriesEvent


class Pairwise(PipeLine):
    _slots__ = (
        'lhs_name',
        'rhs_name',
        'func',
        '__shape'
    )

    @staticmethod
    def get_name(indicator_name, input_lhs, input_rhs, input_key, *args):
        return PipeLine.get_name(indicator_name,
                                 inputs=[input_lhs, input_rhs],
                                 input_key=input_key, *args)

    def __init__(self, input_lhs, input_rhs, func, name, length=1, input_key='close', desc="Pairwise"):
        super(Pairwise, self).__init__(name, [input_lhs, input_rhs], input_key, length=length, desc=desc)
        self.lhs_name = PipeLine.get_input_name(input_lhs)
        self.rhs_name = PipeLine.get_input_name(input_rhs)
        self.func = func

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

        super(Pairwise, self).update_all()

    def on_update(self, event: DataSeriesEvent):
        super(Pairwise, self).on_update(event)
        result = {}
        result['timestamp'] = event.timestamp
        if self.inputs[0].size() >= self.length:
            if self.all_filled():
                x = self.cache[self.lhs_name][-self.length:] if self.length > 1 else self.cache[self.lhs_name][-1]
                y = self.cache[self.rhs_name][-self.length:] if self.length > 1 else self.cache[self.rhs_name][-1]
                result[PipeLine.VALUE] = self.func(x, y)
            else:
                result[PipeLine.VALUE] = self._default_output()
        else:
            result[PipeLine.VALUE] = self._default_output()

        self.add(result)

    def _default_output(self):
        na_array = np.empty(shape=self.shape())
        na_array[:] = np.nan
        return na_array

    def shape(self):
        return self.__shape


# print pairwiseTemplate.render({"className" : "Plus",
#                          "func" : "lambda x: x[0, 0]+x[0, 1]"})
#
# print pairwiseTemplate.render({"className" : "Greater",
#                                "func" : "lambda x: x[0, 0] > x[0, 1]"})
#
# print pairwiseTemplate.render({"className" : "GreaterOrEquals",
#                                "func" : "lambda x: x[0, 0] >= x[0, 1]"})
#
# print pairwiseTemplate.render({"className" : "Less",
#                                "func" : "lambda x: x[0, 0] < x[0, 1]"})
#
# print pairwiseTemplate.render({"className" : "LessOrEquals",
#                                "func" : "lambda x: x[0, 0] <= x[0, 1]"})
#
# print pairwiseTemplate.render({"className" : "Equals",
#                                "func" : "lambda x: x[0, 0] == x[0, 1]"})
#
# print pairwiseTemplate.render({"className" : "NotEquals",
#                                "func" : "lambda x: x[0, 0] != x[0, 1]"})

class Plus(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise Plus"):
        super(Plus, self).__init__(input_lhs, input_rhs, func=lambda x, y: x + y,
                                   name=PipeLine.get_name(Plus.__name__, [input_lhs, input_rhs], input_key),
                                   input_key=input_key, desc=desc)


class Minus(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise Minus"):
        super(Minus, self).__init__(input_lhs, input_rhs, func=lambda x, y: x - y,
                                    name=PipeLine.get_name(Minus.__name__, [input_lhs, input_rhs], input_key),
                                    input_key=input_key, desc=desc)


class Times(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise Times"):
        super(Times, self).__init__(input_lhs, input_rhs, func=lambda x, y: x * y,
                                    name=PipeLine.get_name(Times.__name__, [input_lhs, input_rhs], input_key),
                                    input_key=input_key, desc=desc)


class Divides(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise Divdes"):
        super(Divides, self).__init__(input_lhs, input_rhs, func=lambda x, y: x / y,
                                      name=PipeLine.get_name(Divides.__name__, [input_lhs, input_rhs], input_key),
                                      input_key=input_key, desc=desc)


class Greater(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise Greater"):
        super(Greater, self).__init__(input_lhs, input_rhs, func=lambda x, y: x > y,
                                      name=PipeLine.get_name(Greater.__name__, [input_lhs, input_rhs], input_key),
                                      input_key=input_key, desc=desc)


class GreaterOrEquals(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise GreaterOrEquals"):
        super(GreaterOrEquals, self).__init__(input_lhs, input_rhs, func=lambda x, y: x >= y,
                                              name=PipeLine.get_name(GreaterOrEquals.__name__, [input_lhs, input_rhs],
                                                                     input_key),
                                              input_key=input_key, desc=desc)


class Less(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise Less"):
        super(Less, self).__init__(input_lhs, input_rhs, func=lambda x, y: x < y,
                                   name=PipeLine.get_name(Less.__name__, [input_lhs, input_rhs], input_key),
                                   input_key=input_key, desc=desc)


class LessOrEquals(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise LessOrEquals"):
        super(LessOrEquals, self).__init__(input_lhs, input_rhs, func=lambda x, y: x <= y,
                                           name=PipeLine.get_name(LessOrEquals.__name__, [input_lhs, input_rhs],
                                                                  input_key),
                                           input_key=input_key, desc=desc)


class Equals(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise Equals"):
        super(Equals, self).__init__(input_lhs, input_rhs, func=lambda x, y: x == y,
                                     name=PipeLine.get_name(Equals.__name__, [input_lhs, input_rhs], input_key),
                                     input_key=input_key, desc=desc)


class NotEquals(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise NotEquals"):
        super(NotEquals, self).__init__(input_lhs, input_rhs, func=lambda x, y: x != y,
                                        name=PipeLine.get_name(NotEquals.__name__, [input_lhs, input_rhs], input_key),
                                        input_key=input_key, desc=desc)


class Min(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise Min"):
        super(Min, self).__init__(input_lhs, input_rhs, func=lambda x, y: np.min(np.vstack([x, y]), axis=0),
                                  name=PipeLine.get_name(Min.__name__, [input_lhs, input_rhs], input_key),
                                  input_key=input_key, desc=desc)


class Max(Pairwise):
    def __init__(self, input_lhs, input_rhs, input_key='close', desc="Pairwise Max"):
        super(Max, self).__init__(input_lhs, input_rhs, func=lambda x, y: np.max(np.vstack([x, y]), axis=0),
                                  name=PipeLine.get_name(Max.__name__, [input_lhs, input_rhs], input_key),
                                  input_key=input_key, desc=desc)


class PairCorrelation(Pairwise):
    def __init__(self, input_lhs, input_rhs, length, input_key='close', desc="Pairwise PairCorrelation"):
        super(PairCorrelation, self).__init__(input_lhs, input_rhs, length=length,
                                              func=lambda x, y: np.corrcoef(x, y)[0, 1],
                                              name=PipeLine.get_name(PairCorrelation.__name__, [input_lhs, input_rhs],
                                                                     input_key),
                                              input_key=input_key, desc=desc)

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
