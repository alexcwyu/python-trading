import datetime
import pandas as pd

epoch = datetime.datetime.fromtimestamp(0)


# def datetime_to_unixtimemillis(dt: datetime.datetime) -> int:
    # return int((dt - epoch).total_seconds() * 1000)


def datetime_to_unixtimemillis(dt: datetime.datetime) -> int:
    # this look a bit dull but for consistency
    return pd.Timestamp(dt).value // 10 ** 6

# def unixtimemillis_to_datetime(timestamp: int) -> datetime.datetime:
#     return datetime.datetime.fromtimestamp(timestamp / 1000.0)

def unixtimemillis_to_datetime(timestamp: int) -> datetime.datetime:
    pd.to_datetime(timestamp, unit='ms').to_pydatetime()


def datetime_to_timestamp(dt: datetime.datetime) -> int:
    return (dt - epoch).total_seconds()


def timestamp_to_datetime(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp)


def datestr_to_unixtimemillis(datestr: str) -> int:
    if not datestr:
        return None
    return date_to_unixtimemillis(datestr_to_date(datestr))


def datestr_to_date(datestr: str) -> datetime.date:
    if not datestr:
        return None
    datestr = str(datestr)
    return datetime.date(int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:8]))


def date_to_unixtimemillis(d: datetime.date) -> int:
    return int(
        (datetime.datetime.combine(d, datetime.datetime.min.time()) - epoch).total_seconds() * 1000)


def unixtimemillis_to_date(timestamp: int) -> datetime.date:
    return datetime.datetime.fromtimestamp(timestamp / 1000).date()


def date_to_timestamp(d: datetime.date) -> int:
    return (datetime.datetime.combine(d, datetime.datetime.min.time()) - epoch).total_seconds()


def timestamp_to_date(timestamp: int) -> datetime.date:
    return datetime.datetime.fromtimestamp(timestamp).date()

"""
 if the input is pandas's Timestamp
 
 how we convert is 
 [t.value // 10 ** 9 for t in tsframe.index]
 
 but we have to aware that , the index is assumed to be UTC time and the converted datetime will automatically convert 
 to your time zone!
 
 so better we use this (after Python 3.3)
 
 [ t.to_pydatetime().timestamp() for t in df.index]
 
 
 
 Pandas timestamp to int
 idx1 = [t.value // 10 ** 6 for t in df.index]

int to pandas timestamp
    ridx = pd.to_datetime(idx1, unit='ms')
    
datetime to timestamp
pd.Timstamp(now)
"""

