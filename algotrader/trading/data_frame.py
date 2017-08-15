from typing import Dict

import numpy as np
import pandas as pd
import raccoon as rc
from rx.subjects import Subject
from algotrader import Startable, Context

import algotrader.model.time_series2_pb2 as proto
from algotrader.model.model_factory import ModelFactory
from algotrader.model.time_series_pb2 import TimeSeriesUpdateEvent
from algotrader.utils.proto_series_helper import get_proto_series_data, set_proto_series_data, to_np_type, from_np_type
from algotrader.trading.series import Series

class DataFrame(Startable):
    def __init__(self, df_id: str, inst_id: str, series_list=None, series_ids=None, col_ids=None, dtypes=None):

        if not series_list:
            series_list = []
        elif not isinstance(series_list, (set, tuple, list)):
            series_list = [series_list]

        if not series_ids:
            series_ids = [series.series_id for series in series_list]
        elif not isinstance(series_ids, (set, tuple, list)):
            series_ids = [series_ids]

        self.series_dict = {}
        self.col_dict = {}

        for idx, (series, series_id) in enumerate(zip(series_list, series_ids)):
            if not series:
                # TODO try get the protoseries by series_id from DB
                series = None

            if not series:
                if col_ids:
                    if not isinstance(col_ids, (set, tuple, list)):
                        col_id = col_ids
                    else:
                        col_id = col_ids[idx]

                if dtypes:
                    if not isinstance(dtypes, (set, tuple, list)):
                        dtype = dtypes
                    else:
                        dtype = dtypes[idx]

                series = Series(series_id=series_id, df_id=df_id, col_id=col_id, inst_id=inst_id, dtype=dtype)

            if isinstance(series, proto.Series):
                series = Series(proto_series=series)
            elif isinstance(series, pd.Series):
                series = Series(proto_series=series)

            self.series_dict[series.series_id] = series
            self.col_dict[series.col_id] = series

        self.df_id = df_id
        self.inst_id = inst_id
        self.time_list = []
        self.subject = Subject()

    def on_update(self, event: TimeSeriesUpdateEvent):
        self._process_update(event.source, event.item.timestamp, event.item.data)

    def _process_update(self, source, timestamp, data: Dict):
        pass


    def _start(self, app_context: Context) -> None:
        pass

    def _stop(self):
        pass

    def id(self):
        self.df_id

    def add(self, timestamp, data: Dict):
        self.time_list.append(timestamp)
        for col_id, value in data.items():
            self.col_dict[col_id].add(timestamp=timestamp, value=value)
        self.subject.on_next(
            ModelFactory.build_time_series_update_event(source=self.df_id, timestamp=timestamp, data=data))


    def get_last_update_time(self):
        return self.time_list[-1]


    def has_update(self, timestamp):
        # TODO check update time
        return self.time_list and self.time_list[-1] > timestamp


    def get_data_since(self, timestamp):
        # TODO
        pass

    def to_pd_dataframe(self) -> pd.DataFrame:
        """
        Convert to Pandas DataFrame following Pandas's to_ notation

        :return:
        """
        # TODO
        raise NotImplementedError

    @classmethod
    def from_pd_dataframe(cls):
        """
        Construct from Pandas DataFrame
        :return:
        """
        # TODO
        return cls()


