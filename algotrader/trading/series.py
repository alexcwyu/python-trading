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


class Series(rc.Series):
    def __init__(self, proto_series: proto.Series = None,
                 series_id: str = None, df_id: str = None,
                 col_id: str = None, inst_id: str = None, dtype: np.dtype = np.float64):
        if not proto_series:
            # TODO try get the protoseries by series_id from DB
            proto_series = None

        if proto_series:
            super(Series, self).__init__(data=get_proto_series_data(proto_series),
                                         index=pd.to_datetime(list(proto_series.index), unit='ms').tolist(),
                                         data_name=proto_series.col_id,
                                         index_name="timestamp", use_blist=True)
            self.series_id = proto_series.series_id
            self.df_id = proto_series.df_id
            self.col_id = proto_series.col_id
            self.inst_id = proto_series.inst_id
            self.dtype = to_np_type(proto_series.dtype)
        else:
            super(Series, self).__init__(data_name=col_id, index_name="timestamp", use_blist=True)

            self.series_id = series_id
            self.df_id = df_id
            self.col_id = col_id
            self.inst_id = inst_id
            self.dtype = dtype

        self.subject = Subject()

    def on_update(self, event: TimeSeriesUpdateEvent):
        self._process_update(event.source, event.item.timestamp, event.item.data)

    def _process_update(self, source, timestamp, data: Dict):
        pass

    def add(self, timestamp, value):
        self.append_row(timestamp, value)
        # self.subject.on_next(
        #     ModelFactory.build_time_series_update_event(source=self.series_id, timestamp=timestamp,
        #                                                 data={self.col_id: value}))

    def to_proto_series(self) -> proto.Series:
        """
        Convert to Protobuf Series following Pandas's to_ notation
        :return: proto.Series
        """
        proto_series = proto.Series()
        proto_series.series_id = self.series_id
        proto_series.df_id = self.df_id
        proto_series.col_id = self.col_id
        proto_series.inst_id = self.inst_id
        proto_series.dtype = from_np_type(self.dtype)
        proto_series.index.extend([ts.value // 10 ** 6 for ts in list(self.index)])
        set_proto_series_data(proto_series, self.data)
        return proto_series

    @classmethod
    def from_proto_series(cls, proto_series: proto.Series):
        """
        Construct Series from proto series

        :param proto_series:
        :return:
        """
        series = cls()
        series.append_rows(pd.to_datetime(list(proto_series.index), unit='ms').tolist(),
                           get_proto_series_data(proto_series))
        series.data_name = proto_series.col_id
        series.dtype = to_np_type(proto_series.dtype)

        series.series_id = proto_series.series_id
        series.df_id = proto_series.df_id
        series.col_id = proto_series.col_id
        series.inst_id = proto_series.inst_id
        return series

    def to_pd_series(self) -> pd.Series:
        """
        Convert to Pandas Series following Pandas's to_ notation
        :return: pd.Series
        """
        data = self._data
        index = self._index
        pd_series = pd.Series(data=data, index=index, name=self.data_name, dtype=self.dtype)
        pd_series.series_id = self.series_id
        pd_series.df_id = self.df_id
        pd_series.col_id = self.col_id
        pd_series.inst_id = self.inst_id
        return pd_series

    @classmethod
    def from_pd_series(cls, pd_series: pd.Series, series_id = None, df_id = None, col_id = None, inst_id = None):
        """
        Construct Series from pandas's Series

        :param pd_series:
        :return:
        """
        series = cls()
        series.append_rows(pd_series.index.tolist(), pd_series.values.tolist())
        series.data_name = pd_series.name
        series.dtype = pd_series.dtype

        if hasattr(pd_series, 'series_id'):
            series.series_id = pd_series.series_id
        else:
            series.series_id = series_id

        if hasattr(pd_series, 'df_id'):
            series.df_id = pd_series.df_id
        else:
            series.df_id = df_id

        if hasattr(pd_series, 'col_id'):
            series.col_id = pd_series.col_id
        else:
            series.col_id = col_id

        if hasattr(pd_series, 'inst_id'):
            series.inst_id = pd_series.inst_id
        else:
            series.inst_id = inst_id

        return series

    def to_np_array(self):
        """
        Convert to numpy array following Pandas's to_ notation
        :return: numpy array
        """
        return np.fromiter(self._data, dtype=to_np_type(self.dtype))


