import numpy as np
import talib
from typing import Dict

from algotrader.technical import Indicator


def ds_to_high_numpy(ds, idx):
    for k in ds.keys:
        if k.lower() == 'high':
            return np.array(ds.get_by_idx(keys=k, idx=idx))
    return None


def ds_to_low_numpy(ds, idx):
    for k in ds.keys:
        if k.lower() == 'low':
            return np.array(ds.get_by_idx(keys=k, idx=idx))
    return None


def ds_to_open_list(ds, idx):
    for k in ds.keys:
        if k.lower() == 'open':
            return np.array(ds.get_by_idx(keys=k, idx=idx))
    return None


def ds_to_close_numpy(ds, idx):
    for k in ds.keys:
        if k.lower() == 'close':
            return np.array(ds.get_by_idx(keys=k, idx=idx))
    return None


def ds_to_volume_numpy(ds, idx):
    for k in ds.keys:
        if k.lower() == 'volume':
            return np.array(ds.get_by_idx(keys=k, idx=idx))
    return None


def call_talib_with_hlcv(ds, count, talib_func, *args, **kwargs):
    idx = slice(-count, None, None)
    high = ds_to_high_numpy(ds, idx)
    low = ds_to_low_numpy(ds, idx)
    close = ds_to_close_numpy(ds, idx)
    volume = ds_to_volume_numpy(ds, idx)

    if high is None or low is None or low is None or volume is None:
        return None

    return talib_func(high, low, close, volume, *args, **kwargs)


class SMA(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="TALib Simple Moving Average", length=0):
        if time_series:
            super(SMA, self).__init__(time_series=time_series)
        else:
            super(SMA, self).__init__(inputs=inputs, input_keys=input_keys, desc=desc, length=length)
        self.length = self.get_int_config("length", 0)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.first_input.size() >= self.length:
            value = talib.SMA(
                np.array(
                    self.first_input.get_by_idx(keys=self.first_input_keys,
                                                idx=slice(-self.length, None, None))), timeperiod=self.length)

            result[Indicator.VALUE] = value[-1]
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)


class EMA(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="TALib Exponential Moving Average",
                 length=0):
        if time_series:
            super(EMA, self).__init__(time_series=time_series)
        else:
            super(EMA, self).__init__(inputs=inputs, input_keys=input_keys, desc=desc, length=length)
        self.length = self.get_int_config("length", 0)

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}
        if self.first_input.size() >= self.length:
            value = talib.EMA(
                np.array(
                    self.first_input.get_by_idx(keys=self.first_input_keys,
                                                idx=slice(-self.length, None, None))), timeperiod=self.length)

            result[Indicator.VALUE] = value[-1]
        else:
            result[Indicator.VALUE] = np.nan

        self.add(timestamp=timestamp, data=result)


single_ds_list = ["APO", "BBANDS", "CMO", "DEMA", "EMA", "HT_DCPERIOD", "HT_DCPHASE", "HT_PHASOR", "HT_SINE",
                  "HT_TRENDLINE", "HT_TRENDMODE", "KAMA", "LINEARREG", "LINEARREG_ANGLE", "LINEARREG_INTERCEPT"]
