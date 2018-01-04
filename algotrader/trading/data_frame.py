import bisect
from collections import OrderedDict

import numpy as np
import pandas as pd
import raccoon as rc
from pymonad import Monad, Monoid

from algotrader import Startable
# from algotrader.trading.context import ApplicationContext
from algotrader.app import Application
from algotrader.model.frame_pb2 import Frame
from algotrader.technical.function_wrapper import FunctionWithPeriodsName
from algotrader.trading.series import Series, UpdateMode
from algotrader.trading.subscribable import Subscribable


class DataFrame(Subscribable, Startable, Monad, Monoid):
    def __init__(self, df_id=None, provider_id=None, inst_id=None, parent_df_id=None,
                 columns=None, func=None,
                 update_mode: UpdateMode = UpdateMode.ACTIVE_SUBSCRIBE,
                 transient=False,
                 *args, **kwargs):
        """
        Default Ctor, with protobuf obj pls construct by from ctor
        :param df_id:
        :param provider_id:
        :param inst_id:
        :param parent_df_id:
        :param columns:
        :param func:
        :param update_mode:
        :param transient:
        :param args:
        :param kwargs:
        """
        super(DataFrame, self).__init__(value=None, *args, **kwargs)
        self.df_id = df_id
        self.provider_id = provider_id
        self.inst_id = inst_id
        self.rc_df = rc.DataFrame(columns=columns)
        self.series_dict = None
        self.parent_df_id = parent_df_id
        self.func = func
        self.update_mode = update_mode
        self.transient = transient


    def _start(self, app_context = None):
        # TODO: Probably this is useless
        super(DataFrame, self)._start(self.app_context)

        self.app_context.inst_data_mgr.add_frame(self)

        if self.parent_df_id is not None and self.update_mode == UpdateMode.ACTIVE_SUBSCRIBE:
            parent_frame = self.app_context.inst_data_mgr.get_frame(self.parent_df_id)
            self.subcribe_upstream(parent_frame)
        # self.stream = rx.Observable.zip_list(*[s.subject for s in self._series_list]) \
        #     .subscribe(self.on_frame_slice)

    # def on_frame_slice(self, dummy):
    #     logger.debug("[%s] synchronized" % (self.__class__.__name__ ))
    #     self.rc_df.append_row({s.series_id: s.get_location(-1)['value'] for s in self._series_list})
    #     self.notify_downstream()

    def bind(self, func: FunctionWithPeriodsName):
        """
        Bind the function to dataframe, since dataframe is lazy, we will not calculate now
        :param func:
        :return:
        """
        return self.fmap(func)


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
                atr = atrfun * bar
        again in the _start of the stategy so that here we load it from DB for you and the user assign back the
        relationship between two Monads by function.
        """
        func_name = func.name
        columns = func.output_columns
        drv_df_id = "%s(%s)" % (func_name, self.df_id)

        if not isinstance(columns, list):
            columns = list(columns)

        if self.app_context.inst_data_mgr.has_frame(drv_df_id):
            frame = self.app_context.inst_data_mgr.get_frame(drv_df_id)
            frame.func = func
            return frame
        else:
            frame = DataFrame(df_id=drv_df_id, provider_id=self.provider_id, inst_id=self.inst_id, parent_df_id=self.df_id,
                   func=func, columns=columns, update_mode=self.update_mode)

            self.app_context.inst_data_mgr.add_frame(frame, raise_if_duplicate=True)
            return frame


    def evaluate(self):
        if not self.parent_df_id:
            return


        periods = self.func.periods
        parent_frame = self.app_context.inst_data_mgr.get_frame(self.parent_df_id)

        if len(parent_frame) == 0:
            return


        curr_idx = self.index[-1] if len(self) > 0 else -1
        if parent_frame.index[-1] > curr_idx:
            # TODO: Review if we should use linear search for performace?
            idx = bisect.bisect_right(parent_frame.index, curr_idx)

            parent_len = len(parent_frame)

            if parent_len < periods:
                self.append_rows(parent_frame.index[idx:], {col : [np.nan for i in range(parent_len - idx)]
                                                            for col in self.columns})
            else:
                start = idx - periods if idx >= periods else 0
                val = self.func(parent_frame.tail(parent_len - start).to_dict())

                # self.append_rows(parent_series.index[idx:], val[-parent_len + idx:].tolist())
                self.append_rows(parent_frame.index[idx:], val)





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
            return self.rc_df.to_dict(index=False, ordered=True)

    def to_pd_dataframe(self):
        """
        Convert dataframe to pandas dataframe

        :return: pandas DataFrame
        """
        data_dict = self.to_dict(index=False, value_as_series=False)
        return pd.DataFrame(data_dict, columns=self.rc_df.columns,
                            index= pd.to_datetime(self.rc_df.index, unit='ms'))



    @staticmethod
    def pd_df_to_rc_df(pd_df: pd.DataFrame) -> rc.DataFrame:
        columns = pd_df.columns.tolist()
        data = dict()
        pandas_data = pd_df.values.T.tolist()
        for i in range(len(columns)):
            data[columns[i]] = pandas_data[i]
        # index = pd_df.index.tolist()
        index = [ts.value // 10**6 for ts in pd_df.index.tolist()]
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
    def from_series_dict(cls, series_dict: dict):
        """

        :param series_dict:
        :return:
        """
        df = cls()
        df.series_dict = series_dict
        pd_df = pd.DataFrame(data={series.col_id: series.to_pd_series() for series in series_dict.values()})

        series = next(iter(series_dict.values()))

        df.df_id = series.df_id
        df.provider_id = series.provider_id
        df.inst_id = series.inst_id

        df.rc_df = DataFrame.pd_df_to_rc_df(pd_df)
        df.transient = False
        return df

    @classmethod
    def from_rc_dataframe(cls, rc_df: rc.DataFrame, df_id: str, provider_id: str, parent_df_id:str = None):
        """

        :param rc_df:
        :return:
        """
        df = cls()
        df.rc_df = rc_df
        df.df_id = df_id
        df.provider_id = provider_id
        df.parent_df_id = parent_df_id
        return df

    @classmethod
    def from_pd_dataframe(cls, pd_df: pd.DataFrame, df_id:str, provider_id: str, inst_id:str = None, parent_df_id:str = None):
        """
        Convert a pandas dataframe to dataframe

        :param pd_df:
        :return:
        """
        df = cls()
        df.rc_df = DataFrame.pd_df_to_rc_df(pd_df)
        df.df_id = df_id
        df.provider_id = provider_id
        df.parent_df_id = parent_df_id
        df.inst_id = '' if inst_id is None else inst_id

        return df

    def to_series_dict(self, app_context = None):
        """
        :return:
        """
        if self.series_dict:
            return self.series_dict
        else:
            # we 've got fuck here, we have to store the inst_id
            # as we may have dataframe of series with different inst_id
            series_dict = {}
            for col, dlist in self.rc_df.to_dict(index=False, ordered=True).items():
                # TODO: Review this series_id construction
                df_id = self.df_id
                provider_id = self.provider_id
                inst_id = self.inst_id
                series_id = "%s.%s" % (df_id, col)

                series = Series.from_list(dlist, dtype=np.float64, index=self.rc_df.index,
                                                          series_id=series_id, df_id=df_id,
                                                          provider_id=provider_id,
                                                          inst_id=inst_id,
                                                          col_id=col)


                if app_context is not None:
                    if app_context.inst_data_mgr.has_series(series_id):
                        raise RuntimeError("Series id=%s already exist!" % series_id)
                    else:
                        app_context.inst_data_mgr.add_series(series)

                series_dict[col] = series
            return series_dict
            #                          col_id=col, inst_id=None)

    def to_proto_frame(self, app_context):
        bd = Frame()
        bd.df_id = self.df_id
        bd.provider_id = self.provider_id
        bd.inst_id = self.inst_id

        if self.series_dict is None:
            self.series_dict = self.to_series_dict(app_context)

        for col, series in self.series_dict.items():
            bd.series_id_list.append(series.series_id)

        return bd

    @classmethod
    def from_proto_frame(cls, bundle: Frame, app_context):
        series_list = [app_context.inst_data_mgr.get_series(series_id) for series_id in bundle.series_id_list]
        series_dict = {series.col_id: series for series in series_list}
        return DataFrame.from_series_dict(series_dict)

    def to_list_of_lists(self, cols_orders: list = None):
        """
        This method is useful for those charting like StockCharts in HighCharts ( Python wrapped)
        The first column is index

        :return:
        """
        pd_df = self.to_pd_dataframe()
        if cols_orders is not None:
            col_data = pd_df[cols_orders]
        else:
            col_data = pd_df.values
        data = np.hstack((np.transpose(np.matrix(self.index)), col_data))
        return data.tolist()


    def show(self, index=True, **kwargs):
        return self.rc_df.show(index=index)

    @property
    def data(self):
        return self.rc_df.data

    @property
    def columns(self):
        return self.rc_df.columns


    @property
    def index(self):
        return self.rc_df.index

    @property
    def index_name(self):
        return self.rc_df.index_name

    def __getitem__(self, index):
        return self.rc_df.__getitem__(index)

    def __len__(self):
        return len(self.rc_df)

    def tail(self, rows):
        return self.rc_df.tail(rows)

    def head(self, rows):
        return self.rc_df.head(rows)

    def append(self, df):
        if isinstance(df, pd.DataFrame):
            rc_df = DataFrame.pd_df_to_rc_df(df)
            self._append(rc_df)
        elif isinstance(df, DataFrame):
            self._append(df.rc_df)
        elif isinstance(df, rc.DataFrame):
            self.rc_df.append(df)
        else:
            raise RuntimeError("append only support pandas/raccoon and algotrader's DataFrame")

    def _append(self, df: rc.DataFrame):
        self.rc_df.append(df)
        if self.series_dict:
            values = df.to_dict(index=False)
            indexes = df.index
            for col, val in values.items():
                if col in self.series_dict.keys():
                    series = self.series_dict[col]
                    series.append_rows(indexes, val)
                    # series.add(indexes, val)

        self.notify_downstream(None)


    def append_row(self, index, value, new_cols=True):
        # if index in self.rc_df.index and \
        #     self.app_context is not None and \
        #         self.app_context.config.config['Application']['type'] == Application.BackTesting:
        #     return
        if index in self.rc_df.index:
            return

        self._append_row(index, value, new_cols)



    def _append_row(self, index, value, new_cols=True):
        self.rc_df.append_row(index, value, new_cols)
        if self.series_dict:
            for col, val in value.items():
                # TODO: CREATE A NEW ROW!
                if col in self.series_dict.keys():
                    series = self.series_dict[col]
                    series.add(index, val)

        self.notify_downstream(None)

    def append_rows(self, indexes, values, new_cols=True):
        if self.app_context is not None:
            if self.app_context.config.config['Application']['type']:
                pass



        self.rc_df.append_rows(indexes=indexes, values=values, new_cols=new_cols)
        # TODO: Missing the part in series_dict
        if self.series_dict:
            for col, val in values.items():
                if col in self.series_dict.keys():
                    series = self.series_dict[col]
                    series.append_rows(indexes, val)

        self.notify_downstream(None)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            #TODO: Replace with more efficient check without pandas?
            return self.to_pd_dataframe().equals(other.to_pd_dataframe())
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def get(self, indexes=None, columns=None, as_list=False, as_dict=False):
        return self.rc_df.get(indexes, columns, as_list, as_dict)
