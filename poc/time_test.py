import time
import datetime
from algotrader.event.market_data import BarSize
from dateutil.tz import *

epoch = datetime.datetime.fromtimestamp(0)


def get_bar_end_time(timestamp, bar_size):
    return get_bar_start_time(timestamp, bar_size) + bar_size * 1000 -1


def get_bar_start_time(timestamp, bar_size):
    if bar_size < BarSize.D1:
        return (int(timestamp / (bar_size * 1000)) * bar_size * 1000)
    else:
        dt = datetime.datetime.fromtimestamp(timestamp / 1000)
        dt = datetime.datetime(year=dt.year, month=dt.month, day=dt.day)
        next_ts = unix_time_millis(dt)
        return next_ts


def unix_time_millis(dt):
    return int((dt - epoch).total_seconds() * 1000)


def from_unix_time_millis(timestamp):
    return datetime.datetime.fromtimestamp(timestamp / 1000.0)


dt = datetime.datetime.now()
ts = unix_time_millis(dt)
print ts, datetime.datetime.fromtimestamp(ts / 1000.0)

bar_sizes = [
    ("S1 ", BarSize.S1),
    ("S5 ", BarSize.S5),
    ("S15", BarSize.S15),
    ("S30", BarSize.S30),
    ("M1 ", BarSize.M1),
    ("M5 ", BarSize.M5),
    ("M15", BarSize.M15),
    ("M30", BarSize.M30),
    ("H1 ", BarSize.H1),
    ("D1 ", BarSize.D1)
]

for key, value in bar_sizes:
    ts2_start = get_bar_start_time(ts, value)
    ts2_end = get_bar_end_time(ts, value)
    print key, ts2_start, from_unix_time_millis(ts2_start), ts2_end, from_unix_time_millis(ts2_end)
