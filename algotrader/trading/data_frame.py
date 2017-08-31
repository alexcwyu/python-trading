from typing import Dict

import bisect
import warnings
from collections import OrderedDict, namedtuple
import numpy as np
import pandas as pd
import raccoon as rc
from enum import Enum
from pymonad import Monad, Monoid
from algotrader.trading.subscribable import Subscribable
from rx.subjects import Subject
from algotrader import Startable, Context
from algotrader.trading.context import ApplicationContext
import algotrader.model.time_series2_pb2 as proto
from algotrader.model.model_factory import ModelFactory
from algotrader.model.time_series_pb2 import TimeSeriesUpdateEvent
from algotrader.model.series_bundle_pb2 import SeriesBundle
from algotrader.utils.proto_series_helper import get_proto_series_data, set_proto_series_data, to_np_type, from_np_type
from algotrader.trading.series import Series
from algotrader.utils.function_wrapper import FunctionWithPeriodsName
import rx
from algotrader.utils.logging import logger

# TODO: think how we could save the df into the repository? And when?

class CombineMode(Enum):
    ALL_SYNC_ZIP = 1
    ANY_MOST_LATEST = 2


class DataFrame(Subscribable, Startable, Monad, Monoid):
    def __init__(self, df_id : str, series_list : list = None,
                 rc_df : rc.DataFrame = None,
                 mode: CombineMode = CombineMode.ALL_SYNC_ZIP,
                 *args, **kwargs):
        if series_list and rc_df is not None:
            warnings.warn("Cannot enter both series_list and rc_df, rc_df is ignored!", UserWarning)

        self.series_bundle = SeriesBundle()
        self.series_bundle.df_id = df_id
        for id in series_list:
            self.series_bundle.series_list.append(id)

        self.rc_df = rc_df
        self.mode = mode

        # TODO: Review this
        df_index_name = "Timestamp"

        dfa = rc.DataFrame()
        if rc_df is None:
            pd_df = pd.DataFrame(data={series.col_id: series.to_pd_series() for series in series_list})
            self.rc_df = DataFrame.pd_df_to_rc_df(pd_df)

        if not series_list:
            result = rc_df.to_dict(index=False, ordered=True)
            for col, dlist in rc_df.to_dict(index=False, ordered=True).items():
                # TODO: Review this series_id construction
                self._series_list.append(Series.from_list(dlist, np.float64, index=rc_df.index, series_id="%s-%s" % (df_id, col), df_id=df_id,
                                 col_id=col, inst_id=None))

    def append_row(self, index, values, new_cols=True):
        self.rc_df.append_row(index, values, new_cols)

    def _start(self, app_context = None):
        self.stream = rx.Observable.zip_list(*[s.subject for s in self._series_list]) \
            .subscribe(self.on_frame_slice)

    def on_frame_slice(self, dummy):
        logger.debug("[%s] synchronized" % (self.__class__.__name__ ))
        self.rc_df.append_row({s.series_id: s.get_location(-1)['value'] for s in self._series_list})
        self.notify_downstream()

    def bind(self, func: FunctionWithPeriodsName):
        """
        Bind the function to dataframe, since dataframe is lazy, we will not calculate now
        :param func:
        :return:
        """
        func_name = func.__name__
        drv_series_id = "%s(self.series_id)" % func_name
        series = Series(series_id=drv_series_id, df_id=self.df_id, col_id=func_name, inst_id=self.inst_id, func=func,
                        parent_series_id=self.series_id, dtype=self.dtype, update_mode=self.update_mode)
        return series


        func_name = func.__name__
        drv_df_id = "%s(%s,%s)" % (func_name, self.df_id, func.periods)

        # if self.app_context.inst_data_mgr.has_series(drv_series_id):
        #     series = self.app_context.inst_data_mgr.get_series(drv_series_id)
        #     series.func = func
        #     return series
        # else:
        #     series = Series(series_id=drv_series_id, df_id=self.df_id, col_id=func_name, inst_id=self.inst_id, func=func,
        #                     parent_series_id=self.series_id, dtype=self.dtype, update_mode=self.update_mode)
        #
        #     self.app_context.inst_data_mgr.add_series(series, raise_if_duplicate=True)
        #     return series



    def to_dict(self, value_as_series=True, index=True, ordered=False):
        """
        to dict, and this is the function best used to return back a dict of data and
         if value_as_series turned on, we have algotrader.trading.series as value
        :param value_as_series:
        :param index:
        :param ordered:
        :return:
        """
        if value_as_series:
            collection = OrderedDict() if ordered else dict()
            if index:
                collection.update({self._index_name: self._index})
            if ordered:
                data_dict = [(column, self._series_list[i]) for i, column in enumerate(self._columns)]
            else:
                data_dict = {column: self._series_list[i] for i, column in enumerate(self._columns)}
            collection.update(data_dict)
            return collection
        else:
            return super(DataFrame, self).to_dict()

    def to_pd_dataframe(self):
        """
        Convert dataframe to pandas dataframe

        :return: pandas DataFrame
        """
        data_dict = self.to_dict(index=False, value_as_series=False)
        return pd.DataFrame(data_dict, columns=self.columns, index=self.index)

    @staticmethod
    def pd_df_to_rc_df(pd_df: pd.DataFrame) -> rc.DataFrame:
        columns = pd_df.columns.tolist()
        data = dict()
        pandas_data = pd_df.values.T.tolist()
        for i in range(len(columns)):
            data[columns[i]] = pandas_data[i]
        index = pd_df.index.tolist()
        index_name = pd_df.index.name
        index_name = 'index' if not index_name else index_name
        return rc.DataFrame(data=data, columns=columns, index=index, index_name=index_name)

    @staticmethod
    def series_list_to_rc_df(series_list : list) -> rc.DataFrame:
        """
        :param series_list: list of proto series
        :return:
        """
        pd_df = pd.DataFrame(data={series.col_id: series.to_pd_series() for series in series_list})
        return DataFrame.pd_df_to_rc_df(pd_df)


    @classmethod
    def from_pd_dataframe(cls, pd_df: pd.DataFrame):
        """
        Convert a pandas dataframe to dataframe

        :param pd_df:
        :return:
        """
        df = cls()
        df.rc_df = DataFrame.pd_df_to_rc_df(pd_df)
        return df

    @classmethod
    def from_proto_series_bundle(cls, bundle: SeriesBundle, app_context: ApplicationContext= None):
        df = cls()
        df.series_bundle = bundle

        if app_context is not None:
            series_list = [app_context.inst_data_mgr.get_series(series_id) for series_id in bundle.series_id_list]
            df.rc_df = DataFrame.series_list_to_rc_df(series_list)

#
#
#
# class DataFrameOld(Subscribable, Startable, Monad, Monoid):
#     def __init__(self, df_id: str, inst_id: str, series_ids=None, col_ids=None, dtype: np.dtype = np.float64, \
#                  series_list : list = None, columns=None, index=None, index_name='index'):
#
#         if not series_list:
#             series_list = []
#         elif not isinstance(series_list, (set, tuple, list)):
#             series_list = [series_list]
#
#         if not series_ids:
#             series_ids = [series.series_id for series in series_list]
#         elif not isinstance(series_ids, (set, tuple, list)):
#             series_ids = [series_ids]
#
#         self.series_dict = {}
#         self.col_dict = {}
#
#         for idx, (series, series_id) in enumerate(zip(series_list, series_ids)):
#             if not series:
#                 # TODO try get the protoseries by series_id from DB
#                 series = None
#
#             if not series:
#                 if col_ids:
#                     if not isinstance(col_ids, (set, tuple, list)):
#                         col_id = col_ids
#                     else:
#                         col_id = col_ids[idx]
#
#                 if dtypes:
#                     if not isinstance(dtypes, (set, tuple, list)):
#                         dtype = dtypes
#                     else:
#                         dtype = dtypes[idx]
#
#                 series = Series(series_id=series_id, df_id=df_id, col_id=col_id, inst_id=inst_id, dtype=dtype)
#
#             if isinstance(series, proto.Series):
#                 series = Series(proto_series=series)
#             elif isinstance(series, pd.Series):
#                 series = Series(proto_series=series)
#
#             self.series_dict[series.series_id] = series
#             self.col_dict[series.col_id] = series
#
#         self.df_id = df_id
#         self.inst_id = inst_id
#         self.time_list = []
#         self.subject = Subject()
#
#     def on_update(self, event: TimeSeriesUpdateEvent):
#         self._process_update(event.source, event.item.timestamp, event.item.data)
#
#     def _process_update(self, source, timestamp, data: Dict):
#         pass
#
#
#     def _start(self, app_context: Context) -> None:
#         pass
#
#     def _stop(self):
#         pass
#
#     def id(self):
#         self.df_id
#
#     def add(self, timestamp, data: Dict):
#         self.time_list.append(timestamp)
#         for col_id, value in data.items():
#             self.col_dict[col_id].add(timestamp=timestamp, value=value)
#         self.subject.on_next(
#             ModelFactory.build_time_series_update_event(source=self.df_id, timestamp=timestamp, data=data))
#
#
#     def get_last_update_time(self):
#         return self.time_list[-1]
#
#
#     def has_update(self, timestamp):
#         # TODO check update time
#         return self.time_list and self.time_list[-1] > timestamp
#
#
#     def get_data_since(self, timestamp):
#         # TODO
#         pass
#
#     def to_pd_dataframe(self) -> pd.DataFrame:
#         """
#         Convert to Pandas DataFrame following Pandas's to_ notation
#
#         :return:
#         """
#         # TODO
#         raise NotImplementedError
#
#     @classmethod
#     def from_pd_dataframe(cls):
#         """
#         Construct from Pandas DataFrame
#         :return:
#         """
#         # TODO
#         return cls()
#


