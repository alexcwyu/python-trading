import talib

from algotrader.technical.function_wrapper import FunctionWithPeriodsName
from algotrader.utils.data_series import iterable_to_np_array



class TALibFunction(FunctionWithPeriodsName):
    def __init__(self, periods, func, name=None, array_utils=iterable_to_np_array):
        super(TALibFunction, self).__init__(periods=periods, func=func, name=name, array_utils=array_utils)

    def __call__(self, *args, **kwargs):
        return self.func(timeperiod=self.periods, *args, **kwargs)


def talib_function(periods, name):
    def function_wrapper(f):
        return TALibFunction(func=f, periods=periods, name=name)

    return function_wrapper


"""
The following Function Decorator is used to composite with Dataframe
"""
class TALib1Input3OutputFunction(FunctionWithPeriodsName):
    def __init__(self, periods, func, output_cols, input_col='Close', name=None, array_utils=iterable_to_np_array):
        super(TALib1Input3OutputFunction, self).__init__(periods=periods, func=func, name=name,
                                                 output_columns=output_cols,
                                                 array_utils=array_utils)
        self.input_col = input_col

    def __call__(self, data, *args, **kwargs):
        iarr = self.array_utils(data[self.input_col])
        out1, out2, out3 = self.func(iarr, timeperiod=self.periods, *args, **kwargs)
        cols_iter = iter(self.output_columns)
        out_dict = dict()
        out_dict[next(cols_iter)] = out1
        out_dict[next(cols_iter)] = out2
        out_dict[next(cols_iter)] = out3
        return out_dict


class TALibHLCFunction(FunctionWithPeriodsName):
    def __init__(self, periods, func, output_cols, name=None, array_utils=iterable_to_np_array):
        super(TALibHLCFunction, self).__init__(periods=periods, func=func, name=name,
                                               output_columns=output_cols,
                                               array_utils=array_utils)

    def __call__(self, data, *args, **kwargs):
        high = self.array_utils(data['High'])
        low = self.array_utils(data['Low'])
        close = self.array_utils(data['Close'])
        out_arr = self.func(high=high, low=low, close=close, timeperiod=self.periods, *args, **kwargs)
        return {next(iter(self.output_columns)): out_arr.tolist()}


class TALibHLCVFunction(FunctionWithPeriodsName):
    def __init__(self, periods, func, output_cols, name=None, array_utils=iterable_to_np_array):
        super(TALibHLCVFunction, self).__init__(periods=periods, func=func, name=name,
                                               output_columns=output_cols,
                                               array_utils=array_utils)

    def __call__(self, data, *args, **kwargs):
        high = self.array_utils(data['High'])
        low = self.array_utils(data['Low'])
        close = self.array_utils(data['Close'])
        volume = self.array_utils(data['Volume'])
        out_arr = self.func(high=high, low=low, close=close, volume=volume, timeperiod=self.periods, *args, **kwargs)
        return {next(iter(self.output_columns)): out_arr}


class TALibOHLCFunction(FunctionWithPeriodsName):
    def __init__(self, periods, func, output_cols, name=None, array_utils=iterable_to_np_array):
        super(TALibOHLCFunction, self).__init__(periods=periods, func=func, name=name,
                                                output_columns=output_cols,
                                                array_utils=array_utils)

    def __call__(self, data, *args, **kwargs):
        openarr = self.array_utils(data['Open'])
        high = self.array_utils(data['High'])
        low = self.array_utils(data['Low'])
        close = self.array_utils(data['Close'])
        out_arr = self.func(open=openarr, high=high, low=low, close=close, timeperiod=self.periods, *args, **kwargs)
        return {next(iter(self.output_columns)): out_arr}


class TALibHLFunction(FunctionWithPeriodsName):
    def __init__(self, periods, func, output_cols, name=None, array_utils=iterable_to_np_array):
        super(TALibHLFunction, self).__init__(periods=periods, func=func, name=name,
                                                output_columns=output_cols,
                                                array_utils=array_utils)

    def __call__(self, data, *args, **kwargs):
        high = self.array_utils(data['High'])
        low = self.array_utils(data['Low'])
        out_arr = self.func(high=high, low=low, timeperiod=self.periods, *args, **kwargs)
        return {next(iter(self.output_columns)): out_arr}



def talib_hlc_function(periods, name, output_cols):
    def function_wrapper(f):
        return TALibHLCFunction(func=f, periods=periods, name=name, output_cols=output_cols)

    return function_wrapper

def talib_hlcv_function(periods, name, output_cols):
    def function_wrapper(f):
        return TALibHLCVFunction(func=f, periods=periods, name=name, output_cols=output_cols)

    return function_wrapper

def talib_ohlc_function(periods, name, output_cols):
    def function_wrapper(f):
        return TALibOHLCFunction(func=f, periods=periods, name=name, output_cols=output_cols)

    return function_wrapper

def talib_hl_function(periods, name, output_cols):
    def function_wrapper(f):
        return TALibHLFunction(func=f, periods=periods, name=name, output_cols=output_cols)

    return function_wrapper

def talib_1I3O_function(periods, name, input_col, output_cols):
    def function_wrapper(f):
        return TALib1Input3OutputFunction(func=f, periods=periods, name=name, input_col=input_col, output_cols=output_cols)

    return function_wrapper


# some predefined decorated function as example
atr20 = talib_hlc_function(20, 'ATR20', ['atr20'])(talib.ATR)
bbands20 = talib_1I3O_function(5, 'BBBand5', 'Close', ['UBand', 'MBand', 'LBand'])(talib.BBANDS)

