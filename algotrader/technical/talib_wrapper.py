import numpy as np
import talib

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

    def __init__(self, input, input_key=None, length=0, desc="TALib Simple Moving Average"):
        self.length = int(length)
        super(SMA, self).__init__(Indicator.get_name(SMA.__name__, input, input_key, length), input, input_key, desc)

    def on_update(self, data):

        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            value = talib.SMA(
                np.array(
                    self.input.get_by_idx(keys=self.input_keys,
                                          idx=slice(-self.length, None, None))), timeperiod=self.length)

            result[Indicator.VALUE] = value[-1]
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)


class EMA(Indicator):
    __slots__ = (
        'length'
    )

    def __init__(self, input, input_key=None, length=0, desc="TALib Exponential Moving Average"):
        super(EMA, self).__init__(Indicator.get_name(EMA.__name__, input, input_key, length), input, input_key, desc)
        self.length = int(length)
        super(EMA, self).update_all()

    def on_update(self, data):

        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            value = talib.EMA(
                np.array(
                    self.input.get_by_idx(keys=self.input_keys,
                                          idx=slice(-self.length, None, None))), timeperiod=self.length)

            result[Indicator.VALUE] = value[-1]
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)


single_ds_list = ["APO", "BBANDS", "CMO", "DEMA", "EMA", "HT_DCPERIOD", "HT_DCPHASE", "HT_PHASOR", "HT_SINE",
                  "HT_TRENDLINE", "HT_TRENDMODE", "KAMA", "LINEARREG", "LINEARREG_ANGLE", "LINEARREG_INTERCEPT"]
