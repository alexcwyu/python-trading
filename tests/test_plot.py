from unittest import TestCase

from algotrader.chart.plotter import TimeSeriesPlot
from algotrader.model.model_factory import ModelFactory
from algotrader.model.time_series_pb2 import *
from algotrader.trading.data_series import DataSeries
from algotrader.utils.date import datestr_to_unixtimemillis


class PlotTest(TestCase):
    values = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
              45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]

    factory = ModelFactory()

    def __create_plot(self):
        series = DataSeries(time_series=TimeSeries())
        t = 20170101
        for idx, value in enumerate(self.values):
            ts = datestr_to_unixtimemillis(t)
            series.add(timestamp=ts, data={"value": value})
            t = t + 1
        values = series.get_series(["value"])
        plot = TimeSeriesPlot(values)

        return plot

    def test_plot(self):
        plot = self.__create_plot()
        self.assertIsNotNone(plot)
