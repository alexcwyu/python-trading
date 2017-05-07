
import numpy as np
import pandas as pd
from unittest import TestCase

from algotrader.model.model_factory import ModelFactory
from algotrader.model.time_series_pb2 import *
from algotrader.trading.data_series import DataSeries
from algotrader.utils.date import *
from algotrader.chart.plotter import TimeSeriesPlot
import pytz
from tzlocal import get_localzone

class DataSeriesTest(TestCase):
    values = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
              45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]

    factory = ModelFactory()

    def __create_plot(self):
        series = DataSeries(TimeSeries())
        t = 20170101
        for idx, value in enumerate(self.values):
            ts = datestr_to_unixtimemillis(t)
            series.add({"timestamp": ts, "value": value})
            t = t + 1
        values = series.get_series(["value"])
        #
        # time = pd.DatetimeIndex(pd.to_datetime(values["timestamp"], unit='ms')).tz_localize('UTC' ).tz_convert('Asia/Hong_Kong')
        # data = values["value"].reindex(time)
        #pd.to_datetime(values["value"].index, unit='ms').tz_localize('UTC' ).tz_convert('Asia/Hong_Kong')

        data = pd.Series(values.values,
                  index=pd.to_datetime(values.index, unit='ms').tz_localize('UTC' )
                  .tz_convert(get_localzone().zone))
        plot = TimeSeriesPlot(data)

        return plot



    def test_plot(self):
        plot = self.__create_plot()