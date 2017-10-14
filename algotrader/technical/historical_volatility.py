
import numpy as np
from algotrader.technical.function_wrapper import *
from algotrader.technical.rolling_apply import rolling_window


def historical_volatility_function(arr, days_in_year=252):
    if arr.ndim == 1:
        n = arr.shape[0]
        log_ret = np.log(arr[:-1]/arr[1:])
        return np.sqrt(days_in_year / n * np.sum(log_ret**2))
    else:
        n = arr.shape[1]
        log_ret = np.log(arr[:,:-1]/arr[:,1:])
        return np.sqrt(days_in_year / n * np.sum(log_ret**2, axis=1))


def historical_volatility(arr, periods, days_in_year=252):
    result_arr = np.empty_like(arr)
    result_arr[:] = np.NAN
    result_arr[periods-1:] = historical_volatility_function(rolling_window(arr, periods), days_in_year=days_in_year)
    return result_arr


# decorate the function
hvol30 = periods_function(periods=30, name='hvol30')(historical_volatility) # 30 days historical volatility
hvol60 = periods_function(periods=60, name='hvol60')(historical_volatility) # 60 days historical volatility
hvol90 = periods_function(periods=90, name='hvol90')(historical_volatility) # 90 days historical volatility

