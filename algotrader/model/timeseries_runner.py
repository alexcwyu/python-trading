# from typing import Dict
#
# import numpy as np
# import pandas as pd
# import raccoon as rc
# from rx.subjects import Subject
# from algotrader import Startable, Context
#
# import algotrader.model.time_series2_pb2 as proto
# from algotrader.model.model_factory import ModelFactory
# from algotrader.model.time_series_pb2 import TimeSeriesUpdateEvent
#
#
# def get_proto_series_data(proto_series: proto.Series):
#     if proto_series.dtype == proto.DTFloat:
#         data = proto_series.float_data
#     if proto_series.dtype == proto.DTDouble:
#         data = proto_series.double_data
#     if proto_series.dtype == proto.DTInt32:
#         data = proto_series.int32_data
#     if proto_series.dtype == proto.DTInt64:
#         data = proto_series.int64_data
#     if proto_series.dtype == proto.DTBool:
#         data = proto_series.bool_data
#     if proto_series.dtype == proto.DTString:
#         data = proto_series.string_data
#     if proto_series.dtype == proto.DTByteArray:
#         data = proto_series.bytes_data
#     return list(data)
#
#
# def set_proto_series_data(proto_series: proto.Series, data):
#     if proto_series.dtype == proto.DTFloat:
#         proto_series.float_data.extend(list(data))
#     if proto_series.dtype == proto.DTDouble:
#         proto_series.double_data.extend(list(data))
#     if proto_series.dtype == proto.DTInt32:
#         proto_series.int32_data.extend(list(data))
#     if proto_series.dtype == proto.DTInt64:
#         proto_series.int64_data.extend(list(data))
#     if proto_series.dtype == proto.DTBool:
#         proto_series.bool_data.extend(list(data))
#     if proto_series.dtype == proto.DTString:
#         proto_series.string_data.extend(list(data))
#     if proto_series.dtype == proto.DTByteArray:
#         proto_series.bytes_data.extend(list(data))
#
#
# def to_np_type(dtype: int) -> np.dtype:
#     if dtype == proto.DTFloat:
#         return np.float32
#     if dtype == proto.DTDouble:
#         return np.float64
#     if dtype == proto.DTInt32:
#         return np.int32
#     if dtype == proto.DTInt64:
#         return np.int64
#     if dtype == proto.DTBool:
#         return np.bool_
#     if dtype == proto.DTString:
#         return np.str_
#     if dtype == proto.DTByteArray:
#         return np.bytes_
#
#
# def from_np_type(dtype: np.dtype) -> int:
#     if dtype == np.float32:
#         return proto.DTFloat
#     if dtype == np.float64:
#         return proto.DTDouble
#     if dtype == np.int32:
#         return proto.DTInt32
#     if dtype == np.int64:
#         return proto.DTInt64
#     if dtype == np.bool_:
#         return proto.DTBool
#     if dtype == np.str_:
#         return proto.DTString
#     if dtype == np.bytes_:
#         return proto.DTByteArray
#
#
# class Series(rc.Series):
#     def __init__(self, proto_series: proto.Series = None,
#                  series_id: str = None, df_id: str = None,
#                  col_id: str = None, inst_id: str = None, dtype: str = None):
#         if not proto_series:
#             # TODO try get the protoseries by series_id from DB
#             proto_series = None
#
#         if proto_series:
#             super(Series, self).__init__(data=get_proto_series_data(proto_series),
#                                          index=pd.to_datetime(list(proto_series.index), unit='ms').tolist(),
#                                          data_name=proto_series.col_id,
#                                          index_name="timestamp", use_blist=True)
#             self.series_id = proto_series.series_id
#             self.df_id = proto_series.df_id
#             self.col_id = proto_series.col_id
#             self.inst_id = proto_series.inst_id
#             self.dtype = to_np_type(proto_series.dtype)
#         else:
#             super(Series, self).__init__(data_name=col_id, index_name="timestamp", use_blist=True)
#
#             self.series_id = series_id
#             self.df_id = df_id
#             self.col_id = col_id
#             self.inst_id = inst_id
#             self.dtype = dtype
#
#         self.subject = Subject()
#
#     def on_update(self, event: TimeSeriesUpdateEvent):
#         self._process_update(event.source, event.item.timestamp, event.item.data)
#
#     def _process_update(self, source, timestamp, data: Dict):
#         pass
#
#     def add(self, timestamp, value):
#         self.append_row(timestamp, value)
#         self.subject.on_next(
#             ModelFactory.build_time_series_update_event(source=self.series_id, timestamp=timestamp,
#                                                         data={self.col_id: value}))
#
#
# class DataFrame(Startable):
#     def __init__(self, df_id: str, inst_id: str, series_list=None, series_ids=None, col_ids=None, dtypes=None):
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
#     def get_data_since(self, timestamp):
#         # TODO
#         pass
#
#
# # class DataFrame(rc.DataFrame):
# #     def __init__(self, series_list=None, id=None, inst_id=None):
# #         if series_list:
# #             all_index = set()
# #             # data = {}
# #             columns = []
# #             for series in series_list:
# #                 all_index |= set(series.index)
# #                 columns.append(series.id)
# #
# #             index = sorted(all_index)
# #
# #             super(DataFrame, self).__init__(index=index, columns=columns)
# #
# #             for i in index:
# #                 data = {}
# #                 for series in series_list:
# #                     if i in series.index:
# #                         data[series.id] = series[i]
# #                 self.set(indexes=i, values=data)
# #         else:
# #             super(DataFrame, self).__init__()
#
#
# def series_to_proto_series(series: Series) -> proto.Series:
#     proto_series = proto.Series()
#     proto_series.id = series.id
#     proto_series.df_id = series.df_id
#     proto_series.col_id = series.col_id
#     proto_series.inst_id = series.inst_id
#     proto_series.dtype = from_np_type(series.dtype)
#     proto_series.index.extend([ts.value // 10 ** 6 for ts in list(series.index)])
#     set_proto_series_data(proto_series, series.data)
#     return proto_series
#
#
# def series_to_pd_series(series: Series) -> pd.Series:
#     data = series._data
#     index = series._index
#     pd_series = pd.Series(data=data, index=index, name=series.data_name, dtype=series.dtype)
#     pd_series.series_id = series.series_id
#     pd_series.df_id = series.df_id
#     pd_series.col_id = series.col_id
#     pd_series.inst_id = series.inst_id
#     return pd_series
#
#
# def pd_series_to_series(pd_series: pd.Series) -> Series:
#     series = Series()
#     series.append_rows(list(pd_series.index), list(pd_series.data))
#     series.data_name = pd_series.name
#     series.dtype = pd_series.dtype
#
#     if hasattr(pd_series, 'series_id'):
#         series.series_id = pd_series.series_id
#     if hasattr(pd_series, 'df_id'):
#         series.df_id = pd_series.df_id
#     if hasattr(pd_series, 'col_id'):
#         series.col_id = pd_series.col_id
#     if hasattr(pd_series, 'inst_id'):
#         series.inst_id = pd_series.inst_id
#     return series
#
#
# def proto_series_to_series(proto_series: proto.Series) -> Series:
#     series = Series()
#     series.append_rows(pd.to_datetime(list(proto_series.index), unit='ms').tolist(),
#                        get_proto_series_data(proto_series))
#     series.data_name = proto_series.col_id
#     series.dtype = to_np_type(proto_series.dtype)
#
#     series.series_id = proto_series.series_id
#     series.df_id = proto_series.df_id
#     series.col_id = proto_series.col_id
#     series.inst_id = proto_series.inst_id
#     return series
#
#
# def df_to_proto_series(dataframe: DataFrame) -> Dict[str, proto.Series]:
#     data_dict = dataframe.series_dict
#     #index = dataframe.index
#     result = {}
#     for k, v in data_dict.items():
#         series = series_to_proto_series(v)
#         result[k] = series
#     return result
#
#
# def df_to_pd_df(dataframe: DataFrame) -> pd.DataFrame:
#     data_dict = { k : series_to_pd_series(v) for k , v in dataframe.series_dict.items()}
#     df = pd.DataFrame(data_dict)
#     df.df_id = dataframe.df_id
#     df.inst_id = dataframe.inst_id
#     return df
#
#
# def pd_df_to_df(pd_dataframe: pd.DataFrame) -> DataFrame:
#     columns = pd_dataframe.columns.tolist()
#     #data = dict()
#     pandas_data = pd_dataframe.values.T.tolist()
#     series_list = [pd_series_to_series(data) for data in pandas_data]
#
#     #for i in range(len(columns)):
#     #    data[columns[i]] = pandas_data[i]
#     #index = pd_dataframe.index.tolist()
#     #index_name = pd_dataframe.index.name
#     #index_name = 'index' if not index_name else index_name
#
#     if hasattr(pd_dataframe, 'df_id'):
#         df_id = pd_dataframe.df_id
#
#     if hasattr(pd_dataframe, 'inst_id'):
#         inst_id = pd_dataframe.inst_id
#
#     return DataFrame(df_id=df_id, inst_id=inst_id, series_list=series_list)
#
# df_id = "Bar.Daily"
# inst_id ="HSI@SEHK"
#
# proto_series1 = proto.Series()
# proto_series1.series_id = "Bar.Daily.close-HSI@SEHK"
# proto_series1.df_id = df_id
# proto_series1.col_id = "close"
# proto_series1.inst_id = inst_id
# proto_series1.dtype = proto.DTDouble
# proto_series1.index.extend(list(range(1499787464853, 1499887464853, 20000000)))
# proto_series1.double_data.extend(np.random.rand(5))
#
# proto_series2 = proto.Series()
# proto_series2.series_id = "Bar.Daily.open-HSI@SEHK"
# proto_series2.df_id = df_id
# proto_series2.col_id = "open"
# proto_series2.inst_id = inst_id
# proto_series2.dtype = proto.DTDouble
# proto_series2.index.extend(list(range(1499787464853, 1499887464853, 10000000)))
# proto_series2.double_data.extend(np.random.rand(10))
#
# series1 = proto_series_to_series(proto_series1)
# series2 = proto_series_to_series(proto_series2)
#
# pd_series_1 = series_to_pd_series(series1)
# pd_series_2 = series_to_pd_series(series2)
#
# series1_1 = pd_series_to_series(pd_series_1)
# series2_1 = pd_series_to_series(pd_series_2)
#
# df = DataFrame(df_id=df_id, inst_id = inst_id, series_list=[series1_1, series2_1])
#
# pd_df = df_to_pd_df(df)
#
# df2 = pd_df_to_df(pd_df)
#
# #print(df)
# print(pd_df)
# #print(df2)
#
# result = df_to_proto_series(df2)
#
# #print(result)
#
# #
# #
# # print(series1)
# # print(series1_1)
# #
# # print(proto_series1)
# #
# # print(proto_series1_1)
