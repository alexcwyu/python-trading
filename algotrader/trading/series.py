from typing import Dict

import bisect
import datetime
import numpy as np
import pandas as pd
import raccoon as rc
from enum import Enum
from pymonad import Monad, Monoid
from algotrader import Startable, Context

import algotrader.model.time_series2_pb2 as proto
from algotrader.model.model_factory import ModelFactory
from algotrader.model.time_series_pb2 import TimeSeriesUpdateEvent
from algotrader.utils.proto_series_helper import get_proto_series_data, set_proto_series_data, to_np_type, from_np_type
from algotrader.utils.function_wrapper import FunctionWithPeriodsName
from algotrader.trading.subscribable import Subscribable


class UpdateMode(Enum):
    PASSIVE_PATCH = 1,
    ACTIVE_SUBSCRIBE = 2


class Series(rc.Series, Subscribable, Startable, Monad, Monoid):
    def __init__(self, proto_series: proto.Series = None,
                 series_id: str = None, df_id: str = None,
                 col_id: str = None, inst_id: str = None,
                 provider_id: str = None,
                 dtype: np.dtype = np.float64,
                 func=None,
                 parent_series_id: str = None,
                 update_mode: UpdateMode = UpdateMode.ACTIVE_SUBSCRIBE,
                 *args,
                 **kwargs
                 ):
        if not proto_series:
            # TODO try get the protoseries by series_id from DB
            proto_series = None

        if proto_series:
            super(Series, self).__init__(data=get_proto_series_data(proto_series),
                                         index=pd.to_datetime(list(proto_series.index), unit='ms').tolist(),
                                         data_name=proto_series.col_id,
                                         index_name="timestamp", use_blist=True,
                                         value=None,
                                         *args,
                                         **kwargs)
            self.series_id = proto_series.series_id
            self.df_id = proto_series.df_id
            self.col_id = proto_series.col_id
            self.inst_id = proto_series.inst_id
            self.provider_id = proto_series.provider_id
            self.dtype = to_np_type(proto_series.dtype)
        else:
            super(Series, self).__init__(data_name=col_id, index_name="timestamp", use_blist=True, value=None,
                                         *args,
                                         **kwargs)

            self.series_id = series_id
            self.df_id = df_id
            self.col_id = col_id
            self.inst_id = inst_id
            self.provider_id = provider_id
            self.dtype = dtype

        self.func = func
        self.parent_series_id = parent_series_id
        self.update_mode = update_mode

    def _start(self, app_context=None):

        # TODO: Probably this is useless
        super(Series, self)._start(self.app_context)
        self.app_context.inst_data_mgr.add_series(self)

        if self.parent_series_id is not None and self.update_mode == UpdateMode.ACTIVE_SUBSCRIBE:
            parent_series = self.app_context.inst_data_mgr.get_series(self.parent_series_id)
            self.subcribe_upstream(parent_series)

    def add(self, timestamp, value):
        self.append_row(timestamp, value)
        self.notify_downstream(None)
        # self.subject.on_next(
        #     ModelFactory.build_time_series_update_event(source=self.series_id, timestamp=timestamp,
        #                                                 data={self.col_id: value}))

    def bind(self, func: FunctionWithPeriodsName):
        """
        Bind the function to series, since series is lazy, we will not calculate now
        :param func:
        :return:
        """
        # TODO: It seems to be bind that it bind the function to series itself and replace series content?
        #  in this case we have no interest in that, try to use fmap
        func_name = func.__name__
        drv_series_id = "%s(%s,%s)" % (func_name, self.series_id, func.periods)

        if self.app_context.inst_data_mgr.has_series(drv_series_id):
            series = self.app_context.inst_data_mgr.get_series(drv_series_id)
            series.func = func
            return series
        else:
            series = Series(series_id=drv_series_id, df_id=self.df_id, col_id=func_name, inst_id=self.inst_id,
                            func=func,
                            parent_series_id=self.series_id, dtype=self.dtype, update_mode=self.update_mode)

            self.app_context.inst_data_mgr.add_series(series, raise_if_duplicate=True)
            return series

    def fmap(self, func: FunctionWithPeriodsName):
        """
        Applies 'function' to the contents of the functor and returns a new functor value.
        :param func:
        :return: Series as Monad

        Examle usage
        ema20 = emafunc * close
        where the ema20 is the new Monad that came the binding of emafunc and close Monad.

        Since function itself is not serialized in algotrading environment, eventhough we can directly
        retrieve the ema20 series from DB, it is not recommended to do so as the "function" part is missing.

        It is recommended to declare the
                ema20 = emafunc * close
        again in the _start of the stategy so that here we load it from DB for you and the user assign back the
        relationship between two Monads by function.
        """
        func_name = func.name
        drv_series_id = "%s(%s,%s)" % (func_name, self.series_id, func.periods)

        if self.app_context.inst_data_mgr.has_series(drv_series_id):
            series = self.app_context.inst_data_mgr.get_series(drv_series_id)
            series.func = func
            return series
        else:
            series = Series(series_id=drv_series_id, df_id=self.df_id, col_id=func_name, inst_id=self.inst_id,
                            func=func,
                            parent_series_id=self.series_id, dtype=self.dtype, update_mode=self.update_mode)

            self.app_context.inst_data_mgr.add_series(series, raise_if_duplicate=True)
            return series

    def __rmul__(self, func: FunctionWithPeriodsName):
        """
        The 'fmap' operator.
        The following are equivalent:

        aFunctor.fmap(aFunction)
        aFunction * aFunctor

        """
        return self.fmap(func)

    def mplus(self, other):
        """
        The defining operation of the monoid. This method must be overridden in subclasses
            and should meet the following conditions.
               1. x + 0 == 0 + x == x
               2. (x + y) + z == x + (y + z) == x + y + z
            Where 'x', 'y', and 'z' are monoid values, '0' is the mzero (the identity value) and '+' 
            is mplus.
            
        :param other: another instance of Series
        :return: 

        """
        raise NotImplementedError

    def evaluate(self):
        """
        :return:
        """
        if self.parent_series_id is None:
            # TODO: how to handle this? extra checking ?
            return

        periods = self.func.periods
        parent_series = self.app_context.inst_data_mgr.get_series(self.parent_series_id)

        if len(parent_series) == 0:
            return

        curr_idx = self.index[-1] if len(self) > 0 else -1
        if parent_series.index[-1] > curr_idx:
            # TODO: Review if we should use linear search for performace?
            idx = bisect.bisect_right(parent_series.index, curr_idx)

            parent_len = len(parent_series.index)
            # missing_size = parent_len - idx + periods

            if parent_len < periods:
                self.append_rows(parent_series.index[idx:], [np.nan for i in range(parent_len - idx)])
            else:
                start = idx - periods if idx >= periods else 0
                val = self.func(
                    self.func.array_utils(parent_series.tail(parent_len - start).data))

                self.append_rows(parent_series.index[idx:], val[-parent_len + idx:].tolist())

    # def push_to_downstream(self, event):
    #     self.subject.on_next(event)
    #
    # def subcribe_upstream(self, observable):
    #     observable.subject.subscribe(self.on_update)

    def on_update(self, event: TimeSeriesUpdateEvent):
        self.evaluate()

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
        proto_series.provider_id = self.provider_id if self.provider_id else ''
        proto_series.dtype = from_np_type(self.dtype)
        # proto_series.index.extend([ts.value // 10 ** 6 for ts in list(self.index)])
        proto_series.index.extend(list(self.index))
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
        series.append_rows(
            # pd.to_datetime(list(proto_series.index), unit='ms').tolist(),
            list(proto_series.index),
            get_proto_series_data(proto_series))
        series.data_name = proto_series.col_id
        series.dtype = to_np_type(proto_series.dtype)

        series.series_id = proto_series.series_id
        series.df_id = proto_series.df_id
        series.col_id = proto_series.col_id
        series.inst_id = proto_series.inst_id
        series.provider_id = proto_series.provider_id
        return series

    def to_pd_series(self) -> pd.Series:
        """
        Convert to Pandas Series following Pandas's to_ notation
        :return: pd.Series
        """
        data = self._data
        index = self._index
        pd_series = pd.Series(data=data, index=pd.to_datetime(np.fromiter(index, dtype=np.int64), unit='ms'), name=self.data_name, dtype=self.dtype)
        pd_series.series_id = self.series_id
        pd_series.df_id = self.df_id
        pd_series.col_id = self.col_id
        pd_series.inst_id = self.inst_id
        return pd_series

    @classmethod
    def from_pd_series(cls, pd_series: pd.Series, series_id=None, df_id=None, col_id=None, inst_id=None,
                       provider_id=None):
        """
        Construct Series from pandas's Series

        :param pd_series:
        :return:
        """
        series = cls()
        series.append_rows(
            # pd_series.index.tolist(),
            [t.value // 10 ** 6 for t in pd_series.index.tolist()],
            pd_series.values.tolist())
        series.data_name = pd_series.name
        series.dtype = pd_series.dtype

        if hasattr(pd_series, 'series_id'):
            series.series_id = pd_series.series_id
        else:
            if not series_id:
                raise RuntimeError("Please provide series_id")
            series.series_id = series_id

        if hasattr(pd_series, 'df_id'):
            series.df_id = pd_series.df_id
        else:
            if not df_id:
                raise RuntimeError("Please provide df_id")
            series.df_id = df_id

        if hasattr(pd_series, 'col_id'):
            series.col_id = pd_series.col_id
        else:
            if not col_id:
                raise RuntimeError("Please provide col_id")
            series.col_id = col_id

        if hasattr(pd_series, 'inst_id'):
            series.inst_id = pd_series.inst_id
        else:
            if not inst_id:
                raise RuntimeError("Please provide inst_id")
            series.inst_id = inst_id

        if hasattr(pd_series, 'provider_id'):
            series.provider_id = pd_series.provider_id
        else:
            if not provider_id:
                raise RuntimeError("Please provide sourcd_id")
            series.provider_id = provider_id

        return series

    @classmethod
    def from_np_array(cls, ndarray: np.array,
                      index=None, series_id=None, df_id=None, col_id=None, inst_id=None, provider_id=None):
        """
        Construct Series from numpy array

        :param pd_series:
        :return:
        """
        if not index:
            raise Exception("index cannot be None")

        series = cls()
        series.append_rows(index, ndarray.tolist())
        series.data_name = col_id
        series.dtype = from_np_type(ndarray.dtype)
        series.series_id = series_id
        series.df_id = df_id
        series.col_id = col_id
        series.inst_id = inst_id
        series.provider_id = provider_id

        return series

    def to_np_array(self):
        """
        Convert to numpy array following Pandas's to_ notation
        :return: numpy array
        """
        return np.fromiter(self._data, dtype=to_np_type(self.dtype))

    @classmethod
    def from_list(cls, dlist: list, dtype, index=None, series_id=None, df_id=None, col_id=None, inst_id=None,
                  provider_id=None):
        """
        Construct Series from list

        :param dlist: double list
        :return:
        """
        if not index:
            raise Exception("index cannot be None")

        series = cls()
        series.append_rows(index, dlist)
        series.data_name = col_id
        series.dtype = dtype
        series.series_id = series_id
        series.df_id = df_id
        series.col_id = col_id
        series.inst_id = inst_id
        series.provider_id = provider_id

        return series
