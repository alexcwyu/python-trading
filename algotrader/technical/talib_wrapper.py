import talib
from algotrader.technical.function_wrapper import *


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
        out_dict = {next(iter(self.output_columns)): out_arr.tolist()}
        return out_dict


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
        return {next(iter(self.output_columns)) : out_arr}


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
        return {next(iter(self.output_columns)) : out_arr}


class TALibHLFunction(FunctionWithPeriodsName):
    def __init__(self, periods, func, output_cols, name=None, array_utils=iterable_to_np_array):
        super(TALibHLFunction, self).__init__(periods=periods, func=func, name=name,
                                                output_columns=output_cols,
                                                array_utils=array_utils)

    def __call__(self, data, *args, **kwargs):
        high = self.array_utils(data['High'])
        low = self.array_utils(data['Low'])
        out_arr = self.func(high=high, low=low, timeperiod=self.periods, *args, **kwargs)
        return {next(iter(self.output_columns)) : out_arr}



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


# some predefined decorated function as example
atr20 = talib_hlc_function(20, 'ATR20', ['atr20'])(talib.ATR)
