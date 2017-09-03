
import numpy as np

from algotrader.utils.function_wrapper import *

def historical_volatility(arr: np.ndarray) -> float:
    log_ret = np.log(arr[:-1]/arr[1:])
    return np.sum(log_ret**2)

# decorate the function
hvol30 = periods_function(periods=30, name='hvol30')(historical_volatility) # 30 days historical volatility
hvol60 = periods_function(periods=60, name='hvol60')(historical_volatility) # 60 days historical volatility
hvol90 = periods_function(periods=90, name='hvol90')(historical_volatility) # 90 days historical volatility

